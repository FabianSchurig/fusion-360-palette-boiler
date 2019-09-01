export function sendInfoToFusion(adsk, data) {
    if (typeof adsk !== 'undefined') {
        return adsk.fusionSendData('send', JSON.stringify(data)).then(function (response) {
            return JSON.parse(response.replace(/\'/g, '"'));
        });
    }
}

window.fusionJavaScriptHandler = {
    handle: function (action, data) {
        try {
            if (action === 'send') {
                // Update a paragraph with the data passed in.
                document.getElementById('p1').innerHTML = data;
            } else if (action === 'debugger') {
                debugger;
            } else {
                return 'Unexpected command type: ' + action;
            }
        } catch (e) {
            console.log(e);
            console.log('exception caught with command: ' + action + ', data: ' + data);
        }
        return 'OK';
    }
};