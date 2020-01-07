from django import forms

# TODO: This needs improvement
class UserReviewForm(forms.Form):
    rating = forms.ChoiceField(label='Rating', choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    review = forms.CharField(label='Review', max_length=100)
