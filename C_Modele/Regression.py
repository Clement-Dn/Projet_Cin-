

# Importations des librairies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import t
from scipy.stats import shapiro



def regression(dataframe):
    """
    Régression linéaire avec normalisation de la variable cible et des variables continues
    """

    # Avoir la garantie d'avoir toujours le même découpage train/test pour que les commmentaires soient cohérents
    np.random.seed(42)


    ################### Variables catégorielles : transformation en variables binaires
    categorical_columns = ['genre1', 'genre_ind']
    X = pd.DataFrame()

    for col in categorical_columns:
        dummies = pd.get_dummies(dataframe[col], prefix=col, drop_first=True)
        dummies.columns = dummies.columns.str.replace(f'{col}_', '', regex=False)
        X = pd.concat([X, dummies], axis=1)

    # Transformation des True/False en 1/0
    X = X.astype(int)


    ################### Variables continues : normalisation
    # Variable explicatives
    variables_continues = ['nominations', 'prix', 'duration_min']
    scaler_X = StandardScaler()
    X[variables_continues] = scaler_X.fit_transform(dataframe[variables_continues])


    y = dataframe['spectators_rating']
    scaler_y = StandardScaler()
    y_norm = scaler_y.fit_transform(y.values.reshape(-1, 1)).flatten()


    ################### Modèle

    # Découpage des données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y_norm, test_size=0.3, random_state=42)

    # Entraînement du modèle
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # Prédictions sur l'ensemble de test (valeurs normalisées)
    y_pred_norm = lr_model.predict(X_test)

    # récupération des valeurs originales (1 à 5)
    y_pred = scaler_y.inverse_transform(y_pred_norm.reshape(-1, 1)).flatten()
    y_pred = np.clip(y_pred, 1, 5) # Si une prédiction est au-delà de 6, la note est ramenée à 5
    y_test_original = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Métriques sur les valeurs originales
    mse = mean_squared_error(y_test_original, y_pred)
    r2 = r2_score(y_test_original, y_pred)

    print(f'MSE : {mse:.4f}')
    print(f'R² : {r2:.4f}')



    ########### Coefficients et intervalles de confiance (à 95%)
    coefficients = pd.DataFrame({'Variable': X.columns, 'Coefficient': lr_model.coef_})
    coefficients = coefficients.sort_values(by='Coefficient', ascending=False)


    n = X_train.shape[0]
    p = X_train.shape[1]
    ddl = n - p - 1
    t_value = t.ppf(0.975, ddl)  

    # Matrice de covariance des coefficients
    X_train_const = np.c_[np.ones(X_train.shape[0]), X_train]
    XTX_inv = np.linalg.inv(np.dot(X_train_const.T, X_train_const))
    residus = y_train - lr_model.predict(X_train)
    sigma2 = np.sum(residus**2) / ddl
    cov_matrice = sigma2 * XTX_inv

    # Ecart-types et intervalles de confiance
    std_errors = np.sqrt(np.diag(cov_matrice)[1:])  
    confidence_intervals = [
        (coef - t_value * std_err, coef + t_value * std_err)
        for coef, std_err in zip(lr_model.coef_, std_errors)
    ]

    # Affichage des coefficients et intervalles de confiance
    coefficients_df = pd.DataFrame({
        'Variable': X.columns,
        'Coefficient': lr_model.coef_,
        'Lower CI': [ci[0] for ci in confidence_intervals],
        'Upper CI': [ci[1] for ci in confidence_intervals]
    })
    coefficients_df = coefficients_df.sort_values(by='Coefficient', ascending=False)

    print('\nATTENTION : Les coefficients sont ceux de la régression avec les notes normalisées.\n')
    print(coefficients_df)



    ########### Graphiques
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    # Résidus
    residus = y_test_original - y_pred
    sns.histplot(residus, kde=True, ax=axes[0])
    axes[0].set_title('Distribution des résidus')
    axes[0].set_xlabel('Résidus')
    axes[0].set_ylabel('Fréquence')
    
    # Prédiction vs réel
    axes[1].scatter(y_test_original, y_pred, alpha=0.5)
    axes[1].plot([y_test_original.min(), y_test_original.max()], [y_test_original.min(), y_test_original.max()])
    axes[1].set_xlabel('Valeurs réelles')
    axes[1].set_ylabel('Valeurs prédites')
    axes[1].set_title('Valeurs prédites vs valeurs réelles')


    return
