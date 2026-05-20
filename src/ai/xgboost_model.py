import xgboost as xgb

def train_xgb(X_train, y_train):

    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.05
    )

    model.fit(X_train, y_train)

    return model