const slickSettings = {
    infinite: false,
    slidesToShow: 5,
    slidesToScroll: 2,
    responsive: [
        {
            breakpoint: 1024,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 3
            }
        },
        {
            breakpoint: 600,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 2
            }
        },
        {
            breakpoint: 480,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1
            }
        }
    ]
};

const recSlickSettings = {
    infinite: false,
    slidesToShow: 5,
    slidesToScroll: 2,
    responsive: [
        {
            breakpoint: 1024,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 3
            }
        },
        {
            breakpoint: 600,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 2
            }
        },
        {
            breakpoint: 480,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1
            }
        }
    ],
    asNavFor: '.recipe-slider-focus'
};

const focusSlickSettings = {
    infinite: false,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    fade: true,
    asNavFor: '.recipe-slider-recommended'
};

$(window).scroll(function() {
    if (window.scrollY > 150) {
        $('.navbar.fixed-top').css('background-color', '#141414');
    } else {
        $('.navbar.fixed-top').css('background-color', '');
    }
});

$(document).ready(function() {
    $(`a[href='${window.location.pathname}']`).addClass('active');
    $('.recipe-slider-focus').slick(focusSlickSettings);
    $('.recipe-slider-recommended').slick(recSlickSettings);
    $('.recipe-slider').slick(slickSettings);
});
