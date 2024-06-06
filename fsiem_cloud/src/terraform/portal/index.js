exports.handler = function(event, context, callback) {

    // Get request
    const request = event.Records[0].cf.request;

    // Check the method and request and then redirect if required
    // Some Fortinet One flows require us to support receiving POST requests with data in the body.
    // We can't do this with an S3 hosted website so we need to transform this into a GET so that Angular
    // can pull out the data it needs from the query string.
    if (request.method === "POST" && request.uri === "/login") {
                
        // Pull out the body of the POST request as a JSON string
        const bodyData = request.body.data;
        const bodyJSON = JSON.stringify(bodyData);
        
        // Base 64 encode this JSON string so it can be appended to a URL
        let buffer = new Buffer(bodyJSON);
        const bodyBase64 = buffer.toString();
        
        // Append the data as a URL parameter
        const redirect_path = "/accountselected?data=" + bodyBase64;

        // Return a redirect response to the client redirecting a POST to a GET with the body data appended as a base 64 encoded URL parameter
        const response = {
            status: '302',
            statusDescription: 'Found',
            headers: {
                location: [{
                    key: 'Location',
                    value: redirect_path,
                }],
            },
        };
        
        callback(null, response);
    }

    // Continue request processing if redirection not required
    callback(null, request);
};