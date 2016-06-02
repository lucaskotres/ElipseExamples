# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
import datetime

from app.analysis import comfort_workTime, comfort_day, get_annotations, comfort_workTime_totalMonth, status_air

import json


def statusAir(request):
    """Renders the barGraph page."""
    assert isinstance(request, HttpRequest)

    days, acc_days = status_air()
              
    return render(
        request,
        'app/barStatusAir.html',
        {
            'user':'kotres',
            'title':'BMS',
            'titleGraph': 'Acumulado Março (Expediente)',
            'year':datetime.datetime.now().year,
            #Pizza
            'days':days,
            'acc_days': acc_days
        }
    )

def Pizza_WorkTime(request):
    """Renders the barGraph page."""
    assert isinstance(request, HttpRequest)

    days, down, ok, up  = comfort_workTime_totalMonth()
              
    return render(
        request,
        'app/PizzaWorkTime.html',
        {
            'user':'kotres',
            'title':'BMS',
            'titleGraph': 'Acumulado Março (Expediente)',
            'year':datetime.datetime.now().year,
            #Pizza
            'days':days,
            'ok':ok,
            'up':up,
            'down':down
        }
    )


def BarGraph_WorkTime(request):
    """Renders the barGraph page."""
    assert isinstance(request, HttpRequest)

    days, up, down, ok = comfort_workTime()
              
    return render(
        request,
        'app/barGraph3D.html',
        {
            'user':'kotres',
            'title':'BMS',
            'titleGraph': 'Acumulado Março (Expediente)',
            'year':datetime.datetime.now().year,
            #barGraph
            'days':days,
            'ok':ok,
            'up':up,
            'down':down
        }
    )

def BarGraph(request):
    """Renders the barGraph page."""
    assert isinstance(request, HttpRequest)
    days,ok,up,down = comfort_day()
    return render(
        request,
        'app/barGraph.html',
        {
            'user':'kotres',
            'title':'BMS',
            'titleGraph': 'Acumulado Março (Dia)',
            'year':datetime.datetime.now().year,
            #barGraph
            'days':days,
            'ok':ok,
            'up':up,
            'down':down
            
        }
    )




def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    annotations_dates,annotations_Comfort,annotations_SetPoint,annotations_StatusAir, annotations_T_OUT,annotations_WortTime,annotations_NUser,tag_values,tag_dates = get_annotations()

    return render(
        request,
        'app/dashboard.html',
        {
            'user':'kotres',
            'title':'BMS',
            'year':datetime.datetime.now().year,
            #dashboard
            'annotations_dates':annotations_dates,
            'annotations_comfort':annotations_Comfort,
            'annotations_setpoint': annotations_SetPoint,
            'annotations_StatusAir': annotations_StatusAir,
            'annotations_T_OUT': annotations_T_OUT,
            'annotations_WortTime':annotations_WortTime,
            'annotations_NUser': annotations_NUser,
            'tag_datas':tag_values,
            'tag_dates':tag_dates

            
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
