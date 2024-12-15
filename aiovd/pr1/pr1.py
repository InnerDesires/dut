from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col, when
import pandas as pd
import matplotlib.pyplot as plt

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("AutoMPG_LogisticRegression") \
    .getOrCreate()

# Load data
# First create pandas dataframe
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
column_names = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight',
                'acceleration', 'model_year', 'origin', 'car_name']
pdf = pd.read_csv('auto+mpg/auto-mpg.data', 
                 delim_whitespace=True, 
                 names=column_names,
                 quotechar='"',  # Handle quoted car names
                 na_values='?')  

# Convert to Spark DataFrame
df = spark.createDataFrame(pdf)

# Clean the data
df = df.replace('?', None)
df = df.dropna()

# Convert horsepower to numeric
df = df.withColumn("horsepower", col("horsepower").cast("double"))

# Create binary target variable (1 if mpg > median, 0 otherwise)
mpg_median = df.approxQuantile("mpg", [0.5], 0.01)[0]
df = df.withColumn("efficient", 
                  when(col("mpg") > mpg_median, 1.0)
                  .otherwise(0.0))

# Select features
feature_cols = ['cylinders', 'displacement', 'horsepower', 'weight', 'acceleration']

# Create vector assembler
vector_assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features_unscaled"
)

# Create standard scaler
standard_scaler = StandardScaler(
    inputCol="features_unscaled",
    outputCol="features",
    withStd=True,
    withMean=True
)

# Create logistic regression model
lr = LogisticRegression(
    featuresCol="features",
    labelCol="efficient",
    maxIter=10
)

# Create pipeline
pipeline = Pipeline(stages=[
    vector_assembler,
    standard_scaler,
    lr
])

# Split the data
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# Fit the pipeline
model = pipeline.fit(train_data)

# Make predictions
predictions = model.transform(test_data)

# Evaluate the model
evaluator = BinaryClassificationEvaluator(
    labelCol="efficient",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
)

# Calculate AUC-ROC
auc_roc = evaluator.evaluate(predictions)
print(f"AUC-ROC = {auc_roc}")

# Get feature importance
lr_model = model.stages[-1]
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': [abs(x) for x in lr_model.coefficients]
})
feature_importance = feature_importance.sort_values('Importance', ascending=False)

# Visualize feature importance
plt.figure(figsize=(10, 6))
plt.bar(feature_importance['Feature'], feature_importance['Importance'])
plt.xticks(rotation=45)
plt.title('Feature Importance in Predicting Car Efficiency')
plt.tight_layout()
plt.show()

# Print model summary
trainingSummary = lr_model.summary

# Print accuracy and other metrics
print("Accuracy:", trainingSummary.accuracy)
print("\nConfusion Matrix:")
predictions.groupBy("efficient", "prediction").count().show()

# Print other metrics
print("\nModel Metrics:")
print(f"Accuracy: {trainingSummary.accuracy}")
print(f"Area Under ROC: {trainingSummary.areaUnderROC}")

# Stop Spark session
spark.stop()
