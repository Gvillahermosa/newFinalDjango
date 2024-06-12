// static/users/scripts/trans_report.js

// Include jQuery and Bootstrap JS (make sure these libraries are loaded before this script)
$(document).ready(function(){
    // Django template tag is not directly usable in a JS file, 
    // so we need to pass the necessary context via the template
    if (window.alumniRequestsExist) {
        $('#resultToast').toast('show');
    }
});
