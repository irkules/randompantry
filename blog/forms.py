from django import forms

# TODO: This needs improvement
class UserReviewForm(forms.Form):
    rating = forms.ChoiceField(label='Rating', choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    review = forms.CharField(label='Review', max_length=100)

class RecipeCreateForm(forms.Form):
    name = forms.CharField(label='Name', max_length=50)
    desc = forms.CharField(label='Description', max_length=500, required=False)
    ingrs = forms.CharField(label='Ingredients (Seperated by ",")', max_length=500)
    tags = forms.CharField(label='Tags (Seperated by ",")', max_length=500, required=False)
    calorie = forms.FloatField(label='Calories (Amount per Serving)', min_value=0, max_value=1000)
    fat = forms.FloatField(label='Total Fat (% Daily Value)', min_value=0, max_value=1000)
    sugar = forms.FloatField(label='Sugar (% Daily Value)', min_value=0, max_value=1000)
    sodium = forms.FloatField(label='Sodium (% Daily Value)', min_value=0, max_value=1000)
    protein = forms.FloatField(label='Protein (% Daily Value)', min_value=0, max_value=1000)
    sat_fat = forms.FloatField(label='Saturated Fat (% Daily Value)', min_value=0, max_value=1000)
    carbo = forms.FloatField(label='Total Carbohydrate (% Daily Value)', min_value=0, max_value=1000)
    calorie_level = forms.IntegerField(label='Calorie Level (0-2)', min_value=0, max_value=2)
    minutes = forms.IntegerField(label='Minutes', min_value=1, max_value=5000)
    steps = forms.CharField(label='Steps (Seperated by ",")')
    img_url = forms.URLField(label='Image URL')
