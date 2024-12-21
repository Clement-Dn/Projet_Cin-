import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error

def create_dummies_from_genres(df, genre_columns):
    """
    Crée des colonnes de variables fictives (dummies) à partir des colonnes contenant des genres.

    Args:
        df (pd.DataFrame): Le DataFrame contenant les colonnes de genres.
        genre_columns (list): Liste des noms de colonnes contenant les genres.

    Returns:
        pd.DataFrame: Le DataFrame enrichi avec les colonnes dummies.
    """
    # Concaténation de toutes les colonnes de genres
    all_genres = pd.concat([df[col] for col in genre_columns])
    
    # Extraction des genres uniques
    unique_genres = all_genres.dropna().unique()

    # Création des colonnes dummy
    for genre in unique_genres:
        df[genre] = df[genre_columns].apply(lambda x: genre in x.values, axis=1).astype(int)

    return df




def lasso_regression(data, target_column):
    # Charger les données
    data['femme'] = data['genre_ind'].apply(lambda x: 1 if x == 'f' else 0)
    data = data[['press_rating','femme','devis','annee','duration_min','prix','nominations']]


    # Remplacer les valeurs manquantes par 0
    data.fillna(0, inplace=True)

    # Sélectionner la colonne cible et les caractéristiques
    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Garder uniquement les colonnes numériques
    X = X.select_dtypes(include=['int64', 'float64'])

    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normaliser les données
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Paramètres pour GridSearchCV
    param_grid = {
        'alpha': np.logspace(-4, 4, 50)  # Tester une gamme de valeurs pour alpha
    }

    print("Etape LASSO")
    # Régression LASSO avec GridSearchCV
    lasso = Lasso()
    grid_search = GridSearchCV(estimator=lasso, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    # Meilleur alpha trouvé par GridSearchCV
    best_alpha = grid_search.best_params_['alpha']
    print(f"Meilleur alpha trouvé : {best_alpha}")

    # Entraîner le modèle avec le meilleur alpha
    lasso_best = Lasso(alpha=best_alpha)
    lasso_best.fit(X_train, y_train)

    # Prédire sur l'ensemble de test
    y_pred = lasso_best.predict(X_test)

    # Évaluer le modèle
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error avec meilleur alpha : {mse}")

    # Coefficients LASSO
    lasso_coefs = lasso_best.coef_

    # Variables avec des coefficients différents de 0
    selected_features = X.columns[lasso_coefs != 0]
    print("Variables sélectionnées :", selected_features.tolist())

    # Graphique des coefficients en fonction d'alpha
    coefficients = []
    alphas = np.logspace(-4, 4, 50)
    for alpha in alphas:
        lasso = Lasso(alpha=alpha, max_iter=10000)
        lasso.fit(X_train, y_train)
        coefficients.append(lasso.coef_)

    coefficients = np.array(coefficients)

    plt.figure(figsize=(10, 6))
    for i in range(coefficients.shape[1]):
        plt.plot(alphas, coefficients[:, i], label=f'Feature {X.columns[i]}')

    plt.xscale('log')
    plt.xlabel('lambda en log')
    plt.ylabel('Valeurs des coefficients')
    plt.title('Valeurs des coefficients en fonction du lambda dans une régression Lasso')
    plt.axhline(0, color='black', linestyle='--', linewidth=0.7)
    plt.legend(loc='best', bbox_to_anchor=(1.05, 1), fontsize='small')
    plt.tight_layout()
    plt.show()
    print(data)

