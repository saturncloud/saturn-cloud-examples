# Linear Regression with cuML and cuDF

**Linear Regression** is a simple machine learning model where the response y is modelled by a linear combination of the predictors in X.

The model can take array-like objects, either in host as NumPy arrays or in device (as Numba or cuda_array_interface-compliant), as well as cuDF DataFrames as the input. 

For information about cuDF, refer to the [cuDF documentation](https://docs.rapids.ai/api/cudf/stable).

For information about cuML's linear regression API: https://rapidsai.github.io/projects/cuml/en/stable/api.html#cuml.LinearRegression

[Based of cuml example notebook](https://github.com/rapidsai/cuml/blob/ddbeb36adc511a2dc9bde55e5effe749372aaf66/notebooks/linear_regression_demo.ipynb)

