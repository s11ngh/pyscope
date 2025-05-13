class ConstraintScore:
    def __init__(self, name, weight=1.0):
        self.name = name
        self.weight = weight
        self.score = 0.0
        self.passed = False
        self.details = {}

def check_constraints_with_scoring(observatory, target, times, constraints):
    """
    Check constraints and return both boolean pass/fail and scoring information.
    
    Args:
        observatory (Observer): The observatory object
        target (FixedTarget): The target to check
        times (list): List of times to check
        constraints (list): List of constraints to check
        
    Returns:
        tuple: (bool, list[ConstraintScore])
    """
    scores = []
    overall_pass = True
    
    for constraint in constraints:
        score = ConstraintScore(constraint.__class__.__name__)
        
        try:
            # Get raw constraint results
            results = constraint(observatory, target, times=times)
            
            # For boolean constraints, just pass/fail
            if hasattr(constraint, 'boolean_constraint') and constraint.boolean_constraint:
                score.passed = all(results)
                score.score = 1.0 if score.passed else 0.0
            else:
                # For scoring constraints, calculate quality score
                if isinstance(constraint, astroplan.AltitudeConstraint):
                    altitudes = [observatory.altaz(time, target).alt for time in times]
                    min_alt = min(altitudes)
                    max_alt = max(altitudes)
                    score.score = min_alt.value / constraint.min.value
                    score.details = {
                        'min_altitude': min_alt.value,
                        'max_altitude': max_alt.value,
                        'constraint_min': constraint.min.value
                    }
                elif isinstance(constraint, astroplan.AirmassConstraint):
                    airmasses = [observatory.altaz(time, target).secz for time in times]
                    max_airmass = max(airmasses)
                    score.score = constraint.max / max_airmass
                    score.details = {
                        'max_airmass': max_airmass,
                        'constraint_max': constraint.max
                    }
                elif isinstance(constraint, astroplan.MoonSeparationConstraint):
                    separations = [get_moon_separation(observatory, target, time) for time in times]
                    min_sep = min(separations)
                    score.score = min_sep.value / constraint.min.value
                    score.details = {
                        'min_separation': min_sep.value,
                        'constraint_min': constraint.min.value
                    }
                
                score.passed = score.score >= 1.0
            
            scores.append(score)
            if not score.passed:
                overall_pass = False
                
        except Exception as e:
            score.passed = False
            score.score = 0.0
            score.details = {'error': str(e)}
            scores.append(score)
            overall_pass = False
            
    return overall_pass, scores