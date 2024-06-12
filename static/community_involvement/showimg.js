var loadFile = function (event) {
    var images = document.getElementById('output');
    images.src = URL.createObjectURL(event.target.files[0]);
};
