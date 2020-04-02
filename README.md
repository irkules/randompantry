
![randompantry](./randompantry.png)


# Random Pantry, A Recipe Recommender System

[![website](https://img.shields.io/website?url=https%3A%2F%2Frandompantry.herokuapp.com)](https://randompantry.live)
[![travis](https://img.shields.io/travis/com/irkules/randompantry)]()
[![last-commit](https://img.shields.io/github/last-commit/irkules/randompantry)](https://github.com/irkules/randompantry/commits/master)

Random Pantry is a recipe recommender system that uses machine learning algorithms. It is designed to give you recipes that you will enjoy!


## Usage

### Access
- Website URL: https://randompantry.live
  
  Active Hours: 09:00 - 17:00 Pacific Time (PT)

### Rating a Recipe

### Clearing all ratings (for Global User only)

### Getting Recommendations

### Refreshing Recommendations (Manually)

### Getting Similar Recipes

### Refreshing Similar Recipes (Manually)

### Tuning Recommendations (SVD++)
- n_factors - The number of latent factors
- n_epochs - The number of steps or iterations for Stochastic Gradient Descent algorithm
- lr_all - The learning rate or step size for for all parameters
- reg_all - The regularization term for all parameters

### Tuning Recommendations (Neural Network)


## Technologies
### Languages & Frameworks
* [Angular](https://angular.io/)
* [Django](https://www.djangoproject.com/)
* [Python](https://www.python.org)
* [TypeScript](https://www.typescriptlang.org/)

### Machine Learning
* [pandas](https://pandas.pydata.org/)
* [scikit-learn](https://scikit-learn.org) - Truncated SVD and K-Nearest Neighbours
* [SurPRISE](http://surpriselib.com/) - SVD++

### Database
* [PostgreSQL](https://www.postgresql.org/)
* [Redis](https://redis.io/) - Backend Cache and Celery Broker

### Others
* [Celery](http://www.celeryproject.org) - Distributed Task Queue
* [Honcho](https://honcho.readthedocs.io/en/latest/) - Procfile-based Application Manager


## Data
* [Food.com Recipes and Interactions](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions) - Kaggle
* [Food.](https://www.food.com/) - Recipe Images


## Contributors
| [![irkules](https://avatars0.githubusercontent.com/u/55762386?s=400&v=4)](https://github.com/irkules) | [![deonnem](https://avatars3.githubusercontent.com/u/42830094?s=460&v=4)](https://github.com/deonnem) | [![irkaal](https://avatars0.githubusercontent.com/u/45277297?s=460&u=655fe8d05bb92cf2bad01027b304227e724a154b&v=4)](https://github.com/irkaal) |
| :-: | :-: | :-: |
| [`irkules`](http://github.com/irkules) | [`deonnem`](http://github.com/deonnem) | [`irkaal`](http://github.com/irkaal) |


## Changes
- Version 1.0
    - Initial implementation of Random Pantry
- Version 2.0
    - Asynchronous Random Pantry with Celery and Honcho!
    - Addition of Angular
    - Migration to Global User
    - Addition of Database Cache
    - Addition of Model Tuning feature
    - Addition of RecipeNet (A Recipe Recommender using Keras)

## Reference Papers
- Francesco Ricci, Lior Rokach, Bracha Shapira, and Paul B. Kantor. Recommender Systems Handbook. 1st edition, 2010.
- Ruslan Salakhutdinov and Andriy Mnih. Probabilistic matrix factorization. 2008. URL: http://papers.nips.cc/paper/3208-probabilistic-matrix-factorization.pdf.
- Yehuda Koren. Factorization meets the neighborhood: a multifaceted collaborative filtering model. 2008. URL: http://www.cs.rochester.edu/twiki/pub/Main/HarpSeminar/Factorization_Meets_the_Neighborhood-_a_Multifaceted_Collaborative_Filtering_Model.pdf.
- Yehuda Koren, Robert Bell, and Chris Volinsky. Matrix factorization techniques for recommender systems. 2009.
