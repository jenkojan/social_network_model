import numpy as np
from social_network import create_network


def run(p_connect, p_break):
    return create_network(p_connect/100, p_break/100)

parameters = {
    'p_connect': [0, 50],
    'p_break': [0, 60]
}
num_steps = 5

key_0 = 'p_connect'
key_1 = 'p_break'
print(parameters[key_0])
print(parameters[key_1])

range_0 = range(parameters[key_0][0], parameters[key_0][1], (parameters[key_0][1] - parameters[key_0][0])//num_steps)
range_1 = range(parameters[key_1][0], parameters[key_1][1], (parameters[key_1][1] - parameters[key_1][0])//num_steps)
print(range_0, range_1)
result = list()
for i in range_0:
    tmp_result = list()
    for j in range_1:
        score = run(i, j)
        tmp_result.append(score)
        print("SCORE = ", score)
    result.append(tmp_result)
result = np.array(result)
print(result)
np.save("parameter_tuning", result)