from orion.data import load_signal, load_anomalies

train_data = load_signal("S-1-train")
new_data = load_signal("S-1-new")
ground_truth = load_anomalies("S-1")

train_data.to_csv("./examples/train.csv")
new_data.to_csv("./examples/predict.csv")
ground_truth.to_csv("./examples/test.csv")
