function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}


$(document).ready(function() {
    $('#search_button').click(async function() {
        console.log('Search button is clicked');
        var prompt = $('#search_input').val();
        console.log('Search query is: ');
        console.log(prompt);
        var url = ''
        var result_loaded = false

        $('#search_button').prop("disabled", true)
        $('#search_button').html("Search Results Loading..")

        console.log('Before POSTing');
        const data = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                'prompt': prompt
            })
        })
        let waiting_for_result = true;
        while (waiting_for_result) {
            redirect_url = data['url'];
            console.log(redirect_url);
            if (redirect_url == null) {
                console.log('Still processing...');
                sleep(1000);
                continue;
            }
            else {
                console.log('Processing complete');
                window.location.replace(redirect_url);
                break;
            }
       };
       $()
    });
});