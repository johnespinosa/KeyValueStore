$(document).ready(function() {    
    $('#UpdateSubmit').click(function() {        
        
        var key_input = $("#UpdateKey").val();
        var value_input = $("#UpdateValue").val();
        
        var form_data = new FormData();
        form_data.append("key_input", key_input);
        form_data.append("value_input", value_input);
        
        $.ajax({
            type: 'POST',
            url: '/update_hashtable',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false
    
        });
    
    });
    
    $('#GetValueSubmit').click(function() {        
        
        var key_input = $("#GetKey").val();
        
        var form_data = new FormData();
        form_data.append("key_input", key_input);
        
        $.ajax({
            type: 'POST',
            url: '/get_value',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success:function(data) {
                var KVPair = JSON.parse(data);
                if(KVPair.hasOwnProperty('value')) {
                    $("#KVResult").html(
                        '<p id = "KeyResult"> Key: ' + KVPair.key + '</p>' + 
                        '<p id = "ValueResult"> Value: ' + KVPair.value + '</p>'  
                    );
                } else {
                    $("#KVResult").html(
                        '<p> You have not set the key "'+ KVPair.key +'" </p>'  
                    );
                }
            }
    
        });
    
    });
        
});