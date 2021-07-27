$(document).ready(function() {
    console.log('Search button is clicked');
    $('#loading').hide()

    $('#search_button').click(function() {
        console.log('Search button is clicked');
        var prompt = $('#search_input').val();
        console.log('Search query is: ');
        console.log(prompt);
        var url = '/'

        $('#loading').show();

        $.post(
            url, 
            {
                'prompt': prompt
            }
        ).fail(function() {
          alert( "There is something unexpected happened. Email hello@ai-camp.org to report your findings." );
        });

    });

    $()
});