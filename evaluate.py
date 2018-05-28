#!/usr/bin/env python3
import sys

positive = 0
negative = 0
true_positive = 0
false_positive = 0
true_negative = 0
false_negative = 0
for line in sys.stdin:
    predicted, actual = line.rstrip('\n').split('\t')
    if 'yes' in predicted and 'yes' in actual:
        true_positive += 1
        positive += 1
    if 'yes' in predicted and 'no' in actual:
        false_positive += 1
        negative += 1
    if 'no' in predicted and 'yes' in actual:
        false_negative += 1
        positive += 1
    if 'no' in predicted and 'no' in actual:
        true_negative += 1
        negative += 1

#true positive rate, sensivity
recall = true_positive / positive

#true negative rate
specificity = true_negative / negative

#positive predictive value
precision = true_positive / (true_positive + false_positive)
negative_predictive_value = true_negative / (true_negative + false_negative)

# false negative rate
miss_rate = 1 - recall  # or false_negative / positive

# false positive rate, (negative miss rate)
fall_out = 1 - specificity  # or false_positive / negative

false_discovery_rate = 1 - precision  # or false_positive/ (false_positive / true_positvie)
false_omission_rate = 1 - negative_predictive_value  # or false_negative / (false_negative + true_negative)
accuracy = (true_positive + true_negative) / (positive + negative)

f1 = 2 * (precision * recall) / (precision + recall)
mcc = (true_positive * true_negative) - (false_positive * false_negative) / (
    (true_positive + false_positive) * (true_positive + false_negative) *
    (true_negative + false_positive) * (true_negative + false_negative))**0.5

print(f"""
   Recall  =  {recall}
Precision  =  {precision}
       F1  =  {f1}
 Accuracy  =  {accuracy}
""")
