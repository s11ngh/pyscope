$(document).ready(function() {
    // Initial load of targets list
    updateTargetsList();

    // Handle form submission
    $('#target-form').on('submit', function(e) {
        e.preventDefault();
        
        const targetData = {
            target: $('#target').val(),
            exposure: parseFloat($('#exposure').val()),
            priority: parseInt($('#priority').val())
        };

        $.ajax({
            url: '/add_target',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(targetData),
            success: function(response) {
                if (response.error) {
                    alert(response.error);
                } else {
                    $('#target-form')[0].reset();
                    updateTargetsList();
                }
            },
            error: function(xhr, status, error) {
                alert('Error adding target: ' + error);
            }
        });
    });
});

function updateTargetsList() {
    $.ajax({
        url: '/list_blocks',
        method: 'GET',
        success: function(blocks) {
            const list = $('#targets-list');
            list.empty();
            
            if (blocks.length === 0) {
                list.append('<div class="list-group-item">No targets added yet</div>');
                return;
            }
            
            blocks.forEach(function(block) {
                list.append(`
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${block.target}</strong>
                                <br>
                                <small>Exposure: ${block.exposure} min, Priority: ${block.priority}</small>
                            </div>
                            <button class="btn btn-sm btn-danger" 
                                    onclick="removeTarget(${block.index})">
                                Remove
                            </button>
                        </div>
                    </div>
                `);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching targets:', error);
        }
    });
}

function removeTarget(index) {
    $.ajax({
        url: '/remove_target',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ index: index }),
        success: function(response) {
            if (response.error) {
                alert(response.error);
            } else {
                updateTargetsList();
            }
        },
        error: function(xhr, status, error) {
            alert('Error removing target: ' + error);
        }
    });
}

function showPlot(plotType) {
    // Show loading state
    $('#plot').hide();
    $('#plot-container').append('<div id="loading" class="text-center">Loading plot...</div>');
    
    $.ajax({
        url: `/plot/${plotType}`,
        method: 'GET',
        success: function(response) {
            $('#loading').remove();
            if (response.error) {
                alert(response.error);
            } else {
                const plot = $('#plot');
                plot.attr('src', 'data:image/png;base64,' + response);
                plot.show();
            }
        },
        error: function(xhr, status, error) {
            $('#loading').remove();
            alert('Error generating plot: ' + error);
        }
    });
}