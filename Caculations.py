#!/usr/bin/env python
# coding: utf-8

def BMI(height,weight):
    bmi = round(weight/(height/100)**2,1)
    if bmi<18.5:
        comment = '體重過輕'
    elif bmi<24:
        comment = '體重正常'
    elif bmi<27:
        comment = '體重過重'
    else:
        comment = '體重肥胖'
    return bmi, comment


def DailyCalories(height,weight,activity):
    bmi, comment = BMI(height,weight)
    if comment == '體重過輕':
        if activity == '輕':
            DC = weight*35
        elif activity == '中':
            DC = weight*40
        else:
            DC = weight*45
    elif comment == '體重正常':
        if activity == '輕':
            DC = weight*30
        elif activity == '中':
            DC = weight*35
        else:
            DC = weight*40
    elif comment == '體重過重':
        if activity == '輕':
            DC = weight*25
        elif activity == '中':
            DC = weight*30
        else:
            DC = weight*35
    else:
        if activity == '輕':
            DC = weight*25
        elif activity == '中':
            DC = weight*30
        else:
            DC = weight*35
    return DC
