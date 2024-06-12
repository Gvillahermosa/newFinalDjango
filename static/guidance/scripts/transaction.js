$(document).ready(function(){
    // Get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    $('#frequency').change(()=>{
        if($('#frequency').val() != "daily"){
            if($('#searchSpecificDate').val()){
                $('#searchSpecificDate').val("")
            }
        }
    })

    // Intercept form submission
    $('#aplySort').on('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        
        // Get the entered ID number
        let frequency = $('#frequency').val();

        console.log(frequency)
        if(frequency == "daily"){
            if($('#searchSpecificDate').val()){
                let selectedDate = $('#searchSpecificDate').val();
                let sortFrom = $('#transactionFrom').val();
                $.ajax({
                    url: '/show_transaction_specific_date/',
                    method: 'POST',
                    data: {'selectedDate': selectedDate, 'transactionFrom': sortFrom},
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    success: function(response) {
                        let tempDiv = document.createElement('div');
                        tempDiv.innerHTML = response;
    
                        // Find the element with the ID 'info'
                        let infoTable = tempDiv.querySelector('#transaction_table');
    
                        // Log the infoTable or manipulate it as needed
                        if (infoTable) {
                            $('#transaction_table').html(infoTable.innerHTML)
                        } else {
                            console.log("Element with ID 'info' not found.");
                        }
                    },
                    error: function(error) {
    
                    }
                });  
            }
            else{
                let sortFrom = $('#transactionFrom').val();
                $.ajax({
                    url: '/daily_montly_guidance_transaction/',
                    method: 'POST',
                    data: {'sorttype': frequency,  'transactionFrom': sortFrom},
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    success: function(response) {
                        let tempDiv = document.createElement('div');
                        tempDiv.innerHTML = response;
    
                        // Find the element with the ID 'info'
                        let infoTable = tempDiv.querySelector('#transaction_table');
    
                        // Log the infoTable or manipulate it as needed
                        if (infoTable) {
                            $('#transaction_table').html(infoTable.innerHTML)
                        } else {
                            console.log("Element with ID 'info' not found.");
                        }
                    },
                    error: function(error) {
    
                    }
                });  
            }     
        }
        else{
            let sortFrom = $('#transactionFrom').val();
            $.ajax({
                url: '/daily_montly_guidance_transaction/',
                method: 'POST',
                data: {'sorttype': frequency,  'transactionFrom': sortFrom},
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(response) {
                    let tempDiv = document.createElement('div');
                    tempDiv.innerHTML = response;

                    // Find the element with the ID 'info'
                    let infoTable = tempDiv.querySelector('#transaction_table');

                    // Log the infoTable or manipulate it as needed
                    if (infoTable) {
                        $('#transaction_table').html(infoTable.innerHTML)
                    } else {
                        console.log("Element with ID 'info' not found.");
                    }
                },
                error: function(error) {

                }
            });  
        }
    });
    $('#searchSpecificDate').change(()=>{
        if($('#searchSpecificDate').val()){
            if($('#frequency').val() != "daily"){
                $('#frequency').val("daily")
            }
        }
    });
});