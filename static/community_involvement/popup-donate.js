let donates = document.querySelectorAll('.show-donate');

$.each(donates, function (index, element) {
    element.addEventListener('click', () => {
        $('.donate-popup').removeClass('none');
        console.log(element.value)
        $('.title').val(element.value)
    })
})

$('.close-popup').click(function () {
    $('.donate-popup').addClass('none');
})

let mode = document.querySelectorAll('#mode');

function loadMode() {
    $('.mode1').css("display", "grid");
}

loadMode()

$.each(mode, function (index, element) {
    element.addEventListener('click', () => {
        if (element.value == "mode1") {
            $('.mode1').css("display", "grid");
            $('.mode2').css("display", "none");
            $('.mode3').css("display", "none");
        }

        if (element.value == "mode2") {
            $('.mode1').css("display", "none");
            $('.mode2').css("display", "grid");
            $('.mode3').css("display", "none");
        }

        if (element.value == "mode3") {
            $('.mode1').css("display", "none");
            $('.mode2').css("display", "none");
            $('.mode3').css("display", "grid");
        }
    })
})

// Gcash
let amount_gcash = 0

$('.amount_gcash').on('change', function () {
    amount_gcash = $(this).find(":selected").val()
});

let gcash_number = document.querySelectorAll('#gcash_number');
let gcash_name = document.querySelectorAll('#gcash_name');

let gcash_num = 0
let gcash_n = ""

$.each(gcash_number, function (index, element) {
    element.addEventListener('keyup', () => {
        gcash_num = element.value
    })
})

$.each(gcash_name, function (index, element) {
    element.addEventListener('keyup', () => {
        gcash_n = element.value
    })
})

$('.nextGcash').click(function () {

    if (gcash_n == "" || amount_gcash == "" || gcash_num == "") {
        alert("Please fill in all the required fields");
    } else {
        $('.bank_mode').css("display", "none")
        $('.volunteer_mode').css("display", "none")

        $('.gcash-form').css("display", "none");
        $('.gcash-img').css("display", "grid");
    }
})

// Bank
let bank_amount = 0

$('.bank_amount').on('change', function () {
    bank_amount = $(this).find(":selected").val()
});


let bank_number = document.querySelectorAll('#bank_number');
let bank_name = document.querySelectorAll('#bank_name');

let bank_num = 0
let bank_n = ""

$.each(bank_number, function (index, element) {
    element.addEventListener('keyup', () => {
        bank_num = element.value
    })
})

$.each(bank_name, function (index, element) {
    element.addEventListener('keyup', () => {
        bank_n = element.value
    })
})

// let bank_card = ""

// $('.bank_card').on('change', function (e) {
//     e.preventDefault()

//     bank_card = $(this).find(":selected").val()

//     if(bank_card == "BPI"){

//         $('#qr_bank img').attr("src", "{{qrcode.gcash.url}}");

//      }

//     //  location.href = ""
// });


$('.nextBank').click(function () {

    if (bank_n == "" || bank_amount == "" || bank_num == "") {
        alert("Please fill in all the required fields");
    } else {
        $('.gcash_mode').css("display", "none")
        $('.volunteer_mode').css("display", "none")

        $('.bank-form').css("display", "none");
        $('.bank-img').css("display", "grid");


    }
})



$('.closeBtn').click(function () {
    window.location.reload();
})