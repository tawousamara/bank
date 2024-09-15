function deleteRow(apropos_id) {
    if (confirm('Are you sure you want to delete this row?')) {
        $.ajax({
            url: '/opportunity/delete_apropos',
            type: 'POST',
            contentType: 'application/json', 
            dataType: 'json', 
            data: JSON.stringify({
                'apropos_id': apropos_id,
                'csrf_token': '<t t-out="request.csrf_token()"/>'
            }),
            success: function(response) {
                console.log(apropos_id)
                if (response.success) {
                    console.log('***************************************')
                    $(buttonElement).closest('tr').remove();
                } else {
                    alert('Error: ' + response.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('Failed to delete the row. Status: ' + textStatus + ', Error: ' + errorThrown);
                console.log('Error details:', jqXHR);
            }
        });
    }
}
