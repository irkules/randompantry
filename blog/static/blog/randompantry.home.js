// lightslider global settings
var sliderSettings = {
    item: 5,
    loop: false,
    slideMove: 2,
    eag: 'cubic-bezier(0.25, 0, 0.25, 1)',
    speed: 600,
    responsive: [
        {
            breakpoint: 800,
            settings: {
                item: 3,
                slideMove: 1,
                slideMargin: 6,
            }
        },
        {
            breakpoint: 480,
            settings: {
                item: 2,
                slideMove: 1
            }
        }
    ]
};

// Intialize sliders
$(document).ready(function() {    
    $('#recSlider').lightSlider(sliderSettings);
    $('#favSlider').lightSlider(sliderSettings);
    $('#makeAgainSlider').lightSlider(sliderSettings);  
    $('#topRatedSlider').lightSlider(sliderSettings);  
    $('#tagSlider_1').lightSlider(sliderSettings);  
    $('#tagSlider_2').lightSlider(sliderSettings);
    $('#tagSlider_3').lightSlider(sliderSettings); 
    $('#nutrSlider').lightSlider(sliderSettings);
});
