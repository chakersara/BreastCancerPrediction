import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler


model = pickle.load(open('prediction/model.pkl','rb'))
S=StandardScaler()
v=S.fit_transform(np.array([[9.504,0,273.9,0.10240,0,0]]))
print(model.predict(v))