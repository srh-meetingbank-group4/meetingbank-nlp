import pandas as pd

# Load the CSV files
train_data = pd.read_csv('F:/SRH Munich/1st sem/Data engineering/Exam/data/meetingbank_train.csv')
test_data = pd.read_csv('F:/SRH Munich/1st sem/Data engineering/Exam/data/meetingbank_test.csv')
val_data = pd.read_csv('F:/SRH Munich/1st sem/Data engineering/Exam/data/meetingbank_validation.csv')

# Print the shape and columns of each DataFrame
print("Train Data:")
print(train_data.shape)
print(train_data.columns)
print()

print("Test Data:")
print(test_data.shape)
print(test_data.columns)
print()

print("Validation Data:")
print(val_data.shape)
print(val_data.columns)