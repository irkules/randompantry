// lightslider global settings
var sliderSettings = {
    item: 5,
    loop: false,
    slideMove: 5,
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
    $('#similarRatingSlider').lightSlider(sliderSettings);
    $('#similarIngrSlider').lightSlider(sliderSettings);
    $('#similarTagsSlider').lightSlider(sliderSettings);
    $('#similarNutrSlider').lightSlider(sliderSettings);
});
