import datetime as dt
import io
from pathlib import Path

import campusdual.settings as settings
import cd_core.models as ccm
import cd_examination.models as exm
import cd_organisation.views as orgv
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tables import TableStyle


@login_required
def switchToDocumentationView(request):

    currUser = request.user
    isStu = False

    if currUser.role == "Stu":
        isStu = True

    pdfList = {"1": "/documents/lecDoc1", "2": "/documents/lecDoc2"}
    if isStu:
        pdfList = {
            "1": "/documents/stuDoc1",
            "2": "/documents/stuDoc2",
            "3": "/documents/stuDoc3",
            "4": "/documents/stuDoc4",
        }

    context = {"isStu": isStu, "pdfList": pdfList}

    return render(request, "documentsBlockManager.html", context=context)


def stuDoc1View(request):

    buffer = createPDF_Immatrikulationsbescheinigung(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=Immatrikulationsbescheinigung.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def stuDoc2View(request):

    buffer = createPDF_Bescheinigung48Bafög(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=Bescheinigung_48BAföG.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def stuDoc3View(request):

    buffer = createPDF_Bescheinigung9Bafög(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=Bescheinigung_9BAföG.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def stuDoc4View(request):

    buffer = createPDF_Notenbescheinigung(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=Notenbescheinigung.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def lecDoc1View(request):

    buffer = createPDF_AnwesenheitVorlesung(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=AnwesenheitslisteVL.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def lecDoc2View(request):

    buffer = createPDF_AnwesenheitPrüfung(request.user)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "filename=AnwesenheitslisteP.pdf"
    response["X-Frame-Options"] = "sameorigin"

    return response


def createPDF_Immatrikulationsbescheinigung(user):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.translate(2 * cm, 2 * cm)

    styles = getStyles()

    insertImageHeader(pdf, styles)

    insertSenderAndDateHeader(pdf, styles, user)

    insertRecipientHeader(pdf, styles, user)

    ref = f"""<b>Studienbescheinigung</b><br/><br/>"""
    insertReference(pdf, styles, ref)

    textBlock1 = Frame(
        0 * cm,
        16 * cm,
        17 * cm,
        1.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock1Story = []
    enrY = int(user.enrollmentDate.strftime("%Y"))
    endY = enrY + 3
    text1 = f"""<font fontSize=8>(und Bescheinigung über die Regelstudienzeit vom 01.10.{enrY} bis 30.09.{endY})</font><br/>
    <font fontSize=12 color="red">- gilt bis auf Weiteres als Verlängerungsbescheinigung für den Studentenausweis -</font>"""
    pRef = Paragraph(text1, style=styles["normal"])
    textBlock1Story.append(pRef)
    textBlock1.addFromList(textBlock1Story, pdf)
    pdf.line(0 * cm, 16 * cm, 17 * cm, 16 * cm)

    textBlock2 = Frame(
        0 * cm,
        11 * cm,
        5 * cm,
        5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock2Story = []

    text2 = f"""<b>{getSalutation(user)}<br/>
    Matrikelnummer<br/>
    geboren am<br/>
    geboren in<br/>
    ist im<br/>
    Semesterdauer<br/>
    Studiengang</b>"""
    pText2 = Paragraph(text2, style=styles["normal"])
    textBlock2Story.append(pText2)
    textBlock2.addFromList(textBlock2Story, pdf)

    textBlock3 = Frame(
        5 * cm,
        11 * cm,
        12 * cm,
        5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock3Story = []
    semester = orgv.getSemester(user)
    if user.seminargroup.rythm == "TP":
        sStart = getattr(user.seminargroup, f"term{semester}_t_start").strftime(
            "%d.%m.%Y"
        )
        sEnd = getattr(user.seminargroup, f"term{semester}_p_end").strftime("%d.%m.%Y")
    else:
        sStart = getattr(user.seminargroup, f"term{semester}_p_start").strftime(
            "%d.%m.%Y"
        )
        sEnd = getattr(user.seminargroup, f"term{semester}_t_end").strftime("%d.%m.%Y")
    text3 = f"""{user.first_name} {user.last_name} ({user.seminargroup.code})<br/>
    {user.registration_number}<br/>
    {user.dateOfBirth.strftime("%d.%m.%Y")}<br/>
    {user.placeOfBirth}<br/>
    0{semester}. Semester<br/>
    {sStart} - {sEnd}<br/>
    {user.seminargroup.course.name}"""
    pText3 = Paragraph(text3, style=styles["normal"])
    textBlock3Story.append(pText3)
    textBlock3.addFromList(textBlock3Story, pdf)

    textBlock4 = Frame(
        0 * cm,
        8 * cm,
        17 * cm,
        1 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock4Story = []
    text4 = f"""<b>als Student*in an der {user.seminargroup.course.institution.headInstitution} immatrikuliert.</b>"""
    pText4 = Paragraph(text4, style=styles["normal"])
    textBlock4Story.append(pText4)
    textBlock4.addFromList(textBlock4Story, pdf)

    insertDisclaimer(pdf, styles, 4)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer


def createPDF_Bescheinigung48Bafög(user):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.translate(2 * cm, 2 * cm)

    styles = getStyles()

    insertImageHeader(pdf, styles, False, True)

    insertSenderAndDateHeader(pdf, styles, user)

    insertRecipientHeader(pdf, styles, user)

    ref = f"""<b>Leistungsbescheinigung nach §48 BAföG</b><br/><br/>"""
    insertReference(pdf, styles, ref)

    textBlock1 = Frame(
        0 * cm,
        9.5 * cm,
        5 * cm,
        8 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock1Story = []
    text1 = f"""<b>{getSalutation(user)}<br/><br/>
    Matrikelnummer<br/><br/>
    geboren am<br/><br/>
    ist Student an der<br/><br/>
    <br/><br/>im Studiengang</b>"""
    pText1 = Paragraph(text1, style=styles["normal"])
    textBlock1Story.append(pText1)
    textBlock1.addFromList(textBlock1Story, pdf)

    textBlock2 = Frame(
        5 * cm,
        9.5 * cm,
        12 * cm,
        8 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock2Story = []
    inst = user.seminargroup.course.institution
    text2 = f"""{user.first_name} {user.last_name}<br/><br/>
    {user.registration_number}<br/><br/>
    {user.dateOfBirth.strftime("%d.%m.%Y")}<br/><br/>
    {inst.headInstitution}<br/>
    {inst.subInstitution}<br/>
    {inst.streetNameAndNumber} in {inst.zipCode} {inst.city}<br/><br/>
    {user.seminargroup.course.name}"""
    pText2 = Paragraph(text2, style=styles["normal"])
    textBlock2Story.append(pText2)
    textBlock2.addFromList(textBlock2Story, pdf)

    textBlock3 = Frame(
        0 * cm,
        5 * cm,
        17 * cm,
        4 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock3Story = []
    text3_1 = f"""<b>und hat bis zum Ausstellungsdatum dieser bescheinigung insgesamt<br/><br/></b>"""
    pText3_1 = Paragraph(text3_1, style=styles["normal"])
    text3_2 = f"""<b><font fontSize=14>{user.ects} ECTS-Punkte</font><br/><br/></b>"""
    pText3_2 = Paragraph(text3_2, style=styles["normal_centered"])
    text3_3 = f"""<b>erreicht.</b>"""
    pText3_3 = Paragraph(text3_3, style=styles["normal"])
    textBlock3Story.append(pText3_1)
    textBlock3Story.append(pText3_2)
    textBlock3Story.append(pText3_3)
    textBlock3.addFromList(textBlock3Story, pdf)

    insertDisclaimer(pdf, styles, 2)

    insertImageFooter(pdf, styles)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer


def createPDF_Bescheinigung9Bafög(user):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.translate(2 * cm, 2 * cm)

    styles = getStyles()

    insertImageHeader(pdf, styles, False, True)

    insertSenderAndDateHeader(pdf, styles, user)

    insertRecipientHeader(pdf, styles, user)

    semester = orgv.getSemester(user)
    ref = f"""<b>Studienbescheinigung für das {semester}. Fachsemester</b><br/>
        <font fontSize=11><b>(Bescheinigung nach §9 BAföG zur Vorlage beim Amt für Ausbildungsförderung)</b></font>"""
    insertReference(pdf, styles, ref)

    textBlock1 = Frame(
        0 * cm,
        7.5 * cm,
        5 * cm,
        9.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock1Story = []
    text1 = f"""Hiermit wird bestätigt, dass<br/><br/>
    <b>{getSalutation(user)}</b><br/><br/>
    Matrikelnummer<br/><br/>
    geboren am<br/><br/>
    seit<br/><br/>
    an der<br/><br/>
    <br/>im Studiengang"""
    pText1 = Paragraph(text1, style=styles["normal"])
    textBlock1Story.append(pText1)
    textBlock1.addFromList(textBlock1Story, pdf)

    textBlock2 = Frame(
        5 * cm,
        7.5 * cm,
        12 * cm,
        9.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock2Story = []
    inst = user.seminargroup.course.institution
    text2 = f"""<br/><br/><b>{user.first_name} {user.last_name}</b><br/><br/>
    {user.registration_number}<br/><br/>
    {user.dateOfBirth.strftime("%d.%m.%Y")} in {user.placeOfBirth}<br/><br/>
    {user.enrollmentDate.strftime("%d.%m.%Y")}<br/><br/>
    {inst.headInstitution}<br/>
    {inst.subInstitution}<br/><br/>
    {user.seminargroup.course.name}"""
    pText2 = Paragraph(text2, style=styles["normal"])
    textBlock2Story.append(pText2)
    textBlock2.addFromList(textBlock2Story, pdf)

    textBlock3 = Frame(
        0 * cm,
        4.5 * cm,
        17 * cm,
        3 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock3Story = []
    text3 = f"""immatrikuliert ist und das Studium voraussichtlich am 30.09.{user.seminargroup.enrollment_year + 3} endet.<br/><br/>
    Der/Die Student*in absolviert sein/ihr Studium in Vollzeit und ist nicht beurlaubt."""
    pText3 = Paragraph(text3, style=styles["normal"])
    textBlock3Story.append(pText3)
    textBlock3.addFromList(textBlock3Story, pdf)

    textBlock4 = Frame(
        0 * cm,
        2.5 * cm,
        8 * cm,
        2.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock4Story = []
    text4 = f"""Angestrebter Studienabschluss als:<br/><br/>
    Zeitraum des Fachsemesters:"""
    pText4 = Paragraph(text4, style=styles["normal"])
    textBlock4Story.append(pText4)
    textBlock4.addFromList(textBlock4Story, pdf)

    textBlock5 = Frame(
        8 * cm,
        2.5 * cm,
        9 * cm,
        2.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock5Story = []
    if user.seminargroup.rythm == "TP":
        sStart = getattr(user.seminargroup, f"term{semester}_t_start").strftime(
            "%d.%m.%Y"
        )
        sEnd = getattr(user.seminargroup, f"term{semester}_p_end").strftime("%d.%m.%Y")
    else:
        sStart = getattr(user.seminargroup, f"term{semester}_p_start").strftime(
            "%d.%m.%Y"
        )
        sEnd = getattr(user.seminargroup, f"term{semester}_t_end").strftime("%d.%m.%Y")

    text5 = f"""{user.seminargroup.course.degree}<br/><br/>
    {sStart} - {sEnd}"""
    pText5 = Paragraph(text5, style=styles["normal"])
    textBlock5Story.append(pText5)
    textBlock5.addFromList(textBlock5Story, pdf)

    insertDisclaimer(pdf, styles, 0.5)

    insertImageFooter(pdf, styles)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer


def createPDF_Notenbescheinigung(user):

    entriesPerSite = 14

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    # Seite 1

    pdf.translate(2 * cm, 2 * cm)

    styles = getStyles()

    insertImageHeader(pdf, styles, False, True)

    insertSenderAndDateHeader(pdf, styles, user)

    textBlock1 = Frame(
        0 * cm,
        21 * cm,
        10 * cm,
        2 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock1Story = []
    text1 = f"""<b>BESCHEINIGUNG ÜBER STUDIENLEISTUNGEN</b>"""
    pText1 = Paragraph(text1, style=styles["normal"])
    textBlock1Story.append(pText1)
    textBlock1.addFromList(textBlock1Story, pdf)

    textBlock2 = Frame(
        0 * cm,
        17.5 * cm,
        5 * cm,
        3.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock2Story = []
    text2 = f"""<font fontSize=8><b>STUDIENGANG:<br/>
    ANGESTREBTER ABSCHLUSS:<br/>
    NAME, VORNAME:<br/>
    GEBURTSDATUM/-ORT:<br/>
    IMMATRIKULATIONSDATUM:<br/>
    MATRIKELNUMMER:</b></font>"""
    pText2 = Paragraph(text2, style=styles["normal_small"])
    textBlock2Story.append(pText2)
    textBlock2.addFromList(textBlock2Story, pdf)

    textBlock3 = Frame(
        5 * cm,
        17.5 * cm,
        12 * cm,
        3.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock3Story = []
    text3 = f"""<font fontSize=8>{user.seminargroup.course.name}<br/>
    {user.seminargroup.course.degree}<br/>
    {user.last_name}, {user.first_name}<br/>
    {user.dateOfBirth.strftime("%d.%m.%Y")} / {user.placeOfBirth}<br/>
    {user.enrollmentDate.strftime("%d.%m.%Y")}<br/>
    {user.registration_number}</font>"""
    pText3 = Paragraph(text3, style=styles["normal_small"])
    textBlock3Story.append(pText3)
    textBlock3.addFromList(textBlock3Story, pdf)

    textBlock4 = Frame(
        0 * cm,
        4.5 * cm,
        17 * cm,
        13 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    textBlock4Story = []

    text4_1 = f"""<b>Modulcode</b>"""
    pText4_1 = Paragraph(text4_1, style=styles["table"])
    text4_2 = f"""<b>Titel des Moduls / Art der Prüfung (1)</b>"""
    pText4_2 = Paragraph(text4_2, style=styles["table"])
    text4_3 = f"""<b>Semester</b>"""
    pText4_3 = Paragraph(text4_3, style=styles["table_centered"])
    text4_4 = f"""<b>Prüfungs- ergebnis (2)</b>"""
    pText4_4 = Paragraph(text4_4, style=styles["table"])
    text4_5 = f"""<b>ECTS Punkte</b>"""
    pText4_5 = Paragraph(text4_5, style=styles["table"])
    tableHeaderData = [[pText4_1, pText4_2, pText4_3, pText4_4, pText4_5]]
    tableHeader = Table(
        tableHeaderData,
        colWidths=[3 * cm, 7.5 * cm, 2 * cm, 2.5 * cm, 2 * cm],
    )
    tableHeader.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    examQuery = exm.ExamRegistration.objects.filter(
        participant=user, result__isnull=False
    ).order_by(
        "examination__module__term", "examination__module__code", "evaluationCompletion"
    )

    if len(examQuery) > 0 and len(examQuery) <= 15:
        tableContentData = []
        for exam in examQuery:
            text4_1 = f"""{exam.examination.module.code}"""
            pText4_1 = Paragraph(text4_1, style=styles["table"])
            if exam.attempt == 1:
                attempt = "EP"
            elif exam.attempt == 2:
                attempt = "W1"
            elif exam.attempt == 3:
                attempt = "W2"
            elif exam.attempt == 4:
                attempt = "AL"
            else:
                attempt = "FL"
            text4_2 = f"""{exam.examination.module.name} ({attempt})"""
            pText4_2 = Paragraph(text4_2, style=styles["table"])
            text4_3 = f"""{exam.examination.module.term}"""
            pText4_3 = Paragraph(text4_3, style=styles["table_centered"])
            text4_4 = f"""{str(exam.result).replace(".", ",")}"""
            pText4_4 = Paragraph(text4_4, style=styles["table_centered"])
            ects = 0
            if exam.result <= 4.0:
                ects = exam.examination.module.ects
            text4_5 = f"""{ects}"""
            pText4_5 = Paragraph(text4_5, style=styles["table_centered"])
            tableContentData.append([pText4_1, pText4_2, pText4_3, pText4_4, pText4_5])
        tableContent = Table(
            tableContentData, colWidths=[3 * cm, 7.5 * cm, 2 * cm, 2.5 * cm, 2 * cm]
        )
        tableContent.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        text6_1 = f""""""
        pText6_1 = Paragraph(text6_1, style=styles["table"])
        text6_2 = f"""<b>Summe:</b>"""
        pText6_2 = Paragraph(text6_2, style=styles["table_centered"])
        text6_3 = f"""{user.ects}"""
        pText6_3 = Paragraph(text6_3, style=styles["table_centered"])
        tableFooterData = [[pText6_1, pText6_2, pText6_3]]
        tableFooter = Table(
            tableFooterData,
            colWidths=[12.5 * cm, 2.5 * cm, 2 * cm],
        )
        tableFooter.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        textBlock4Story.append(tableHeader)
        if len(examQuery) > 0:
            textBlock4Story.append(tableContent)
        textBlock4Story.append(tableFooter)
        textBlock4.addFromList(textBlock4Story, pdf)

        insertDisclaimer(pdf, styles, 2.5)

        textBlock5 = Frame(
            0 * cm,
            2 * cm,
            3 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock5Story = []
        text5 = f"""<b>1) Art der Prüfung:<br/>
        2) Bewertungsskala:</b>"""
        pText5 = Paragraph(text5, style=styles["footnote"])
        textBlock5Story.append(pText5)
        textBlock5.addFromList(textBlock5Story, pdf)

        textBlock6 = Frame(
            3 * cm,
            2 * cm,
            14 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock6Story = []
        text6 = f"""EP - Erstprüfung AL - anerkannte externe Leistung FL - fakultative Leistung W1 - 1. Wiederholungsprüfung W2 - 2. Wiederholungsprüfung<br/>
        1,0 - 1,5 sehr gut 1,6 - 2,5 gut 2,6 - 3,5 befriedigend 3,6 - 4,0 ausreichend 4,1 - 5,0 nicht ausreichend"""
        pText6 = Paragraph(text6, style=styles["footnote"])
        textBlock6Story.append(pText6)
        textBlock6.addFromList(textBlock6Story, pdf)

        textBlock7 = Frame(
            0 * cm,
            1 * cm,
            17 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock7Story = []
        text7 = f"""<font fontSize=10>Bescheinigung über Studienleistungen - Seite 1 von 1</font>"""
        pText7 = Paragraph(text7, style=styles["date"])
        textBlock7Story.append(pText7)
        textBlock7.addFromList(textBlock7Story, pdf)

        insertImageFooter(pdf, styles)

    elif len(examQuery) > entriesPerSite:
        tableContentData = []
        for exam in examQuery[:entriesPerSite]:
            text4_1 = f"""{exam.examination.module.code}"""
            pText4_1 = Paragraph(text4_1, style=styles["table"])
            if exam.attempt == 1:
                attempt = "EP"
            elif exam.attempt == 2:
                attempt = "W1"
            elif exam.attempt == 3:
                attempt = "W2"
            elif exam.attempt == 4:
                attempt = "AL"
            else:
                attempt = "FL"
            text4_2 = f"""{exam.examination.module.name} ({attempt})"""
            pText4_2 = Paragraph(text4_2, style=styles["table"])
            text4_3 = f"""{exam.examination.module.term}"""
            pText4_3 = Paragraph(text4_3, style=styles["table_centered"])
            text4_4 = f"""{str(exam.result).replace(".", ",")}"""
            pText4_4 = Paragraph(text4_4, style=styles["table_centered"])
            ects = 0
            if exam.result <= 4.0:
                ects = exam.examination.module.ects
            text4_5 = f"""{ects}"""
            pText4_5 = Paragraph(text4_5, style=styles["table_centered"])
            tableContentData.append([pText4_1, pText4_2, pText4_3, pText4_4, pText4_5])
        tableContent = Table(
            tableContentData, colWidths=[3 * cm, 7.5 * cm, 2 * cm, 2.5 * cm, 2 * cm]
        )
        tableContent.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        textBlock4Story.append(tableHeader)
        textBlock4Story.append(tableContent)
        textBlock4.addFromList(textBlock4Story, pdf)

        textBlock5 = Frame(
            0 * cm,
            1 * cm,
            17 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock5Story = []
        text5 = f"""<font fontSize=10>Bescheinigung über Studienleistungen - Seite 1 von 2</font>"""
        pText5 = Paragraph(text5, style=styles["date"])
        textBlock5Story.append(pText5)
        textBlock5.addFromList(textBlock5Story, pdf)

        insertImageFooter(pdf, styles)

        # Seite 2

        pdf.showPage()
        pdf.translate(2 * cm, 2 * cm)

        textBlock21 = Frame(
            0 * cm,
            24 * cm,
            10 * cm,
            2 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock21Story = []
        text21 = f"""<b>BESCHEINIGUNG ÜBER STUDIENLEISTUNGEN</b>"""
        pText21 = Paragraph(text21, style=styles["normal"])
        textBlock21Story.append(pText21)
        textBlock21.addFromList(textBlock21Story, pdf)

        textBlock215 = Frame(
            12 * cm,
            25 * cm,
            5 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock215Story = []
        bal = ccm.Institution.objects.filter(
            city=user.seminargroup.course.institution.city
        )[0]
        today = dt.date.today().strftime("%d.%m.%Y")
        text215 = f"""{bal.city}, {today}"""
        pText215 = Paragraph(text215, style=styles["date"])
        textBlock215Story.append(pText215)
        textBlock215.addFromList(textBlock215Story, pdf)

        textBlock22 = Frame(
            0 * cm,
            23 * cm,
            5 * cm,
            2 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock22Story = []
        text22 = f"""<font fontSize=8><b>NAME, VORNAME:<br/>
        MATRIKELNUMMER:</b></font>"""
        pText22 = Paragraph(text22, style=styles["normal_small"])
        textBlock22Story.append(pText22)
        textBlock22.addFromList(textBlock22Story, pdf)

        textBlock23 = Frame(
            5 * cm,
            23 * cm,
            12 * cm,
            2 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock23Story = []
        text23 = f"""<font fontSize=8>{user.last_name}, {user.first_name}<br/>
        {user.registration_number}</font>"""
        pText23 = Paragraph(text23, style=styles["normal_small"])
        textBlock23Story.append(pText23)
        textBlock23.addFromList(textBlock23Story, pdf)

        textBlock4 = Frame(
            0 * cm,
            4.5 * cm,
            17 * cm,
            19 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock4Story = []

        text4_1 = f"""<b>Modulcode</b>"""
        pText4_1 = Paragraph(text4_1, style=styles["table"])
        text4_2 = f"""<b>Titel des Moduls / Art der Prüfung (1)</b>"""
        pText4_2 = Paragraph(text4_2, style=styles["table"])
        text4_3 = f"""<b>Semester</b>"""
        pText4_3 = Paragraph(text4_3, style=styles["table_centered"])
        text4_4 = f"""<b>Prüfungs- ergebnis (2)</b>"""
        pText4_4 = Paragraph(text4_4, style=styles["table"])
        text4_5 = f"""<b>ECTS Punkte</b>"""
        pText4_5 = Paragraph(text4_5, style=styles["table"])
        tableHeaderData2 = [[pText4_1, pText4_2, pText4_3, pText4_4, pText4_5]]
        tableHeader2 = Table(
            tableHeaderData2,
            colWidths=[3 * cm, 7.5 * cm, 2 * cm, 2.5 * cm, 2 * cm],
        )
        tableHeader2.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        tableContentData2 = []
        for exam in examQuery[entriesPerSite:]:
            text4_1 = f"""{exam.examination.module.code}"""
            pText4_1 = Paragraph(text4_1, style=styles["table"])
            if exam.attempt == 1:
                attempt = "EP"
            elif exam.attempt == 2:
                attempt = "W1"
            elif exam.attempt == 3:
                attempt = "W2"
            elif exam.attempt == 4:
                attempt = "AL"
            else:
                attempt = "FL"
            text4_2 = f"""{exam.examination.module.name} ({attempt})"""
            pText4_2 = Paragraph(text4_2, style=styles["table"])
            text4_3 = f"""{exam.examination.module.term}"""
            pText4_3 = Paragraph(text4_3, style=styles["table_centered"])
            text4_4 = f"""{str(exam.result).replace(".", ",")}"""
            pText4_4 = Paragraph(text4_4, style=styles["table_centered"])
            ects = 0
            if exam.result <= 4.0:
                ects = exam.examination.module.ects
            text4_5 = f"""{ects}"""
            pText4_5 = Paragraph(text4_5, style=styles["table_centered"])
            tableContentData2.append([pText4_1, pText4_2, pText4_3, pText4_4, pText4_5])
        tableContent2 = Table(
            tableContentData2, colWidths=[3 * cm, 7.5 * cm, 2 * cm, 2.5 * cm, 2 * cm]
        )
        tableContent2.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        text6_1 = f""""""
        pText6_1 = Paragraph(text6_1, style=styles["table"])
        text6_2 = f"""<b>Summe:</b>"""
        pText6_2 = Paragraph(text6_2, style=styles["table_centered"])
        text6_3 = f"""{user.ects}"""
        pText6_3 = Paragraph(text6_3, style=styles["table_centered"])
        tableFooterData = [[pText6_1, pText6_2, pText6_3]]
        tableFooter = Table(
            tableFooterData,
            colWidths=[12.5 * cm, 2.5 * cm, 2 * cm],
        )
        tableFooter.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )

        textBlock4Story.append(tableHeader2)
        textBlock4Story.append(tableContent2)
        textBlock4Story.append(tableFooter)
        textBlock4.addFromList(textBlock4Story, pdf)

        insertDisclaimer(pdf, styles, 2.5)

        textBlock5 = Frame(
            0 * cm,
            2 * cm,
            3 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock5Story = []
        text5 = f"""<b>1) Art der Prüfung:<br/>
        2) Bewertungsskala:</b>"""
        pText5 = Paragraph(text5, style=styles["footnote"])
        textBlock5Story.append(pText5)
        textBlock5.addFromList(textBlock5Story, pdf)

        textBlock6 = Frame(
            3 * cm,
            2 * cm,
            14 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock6Story = []
        text6 = f"""EP - Erstprüfung AL - anerkannte externe Leistung FL - fakultative Leistung W1 - 1. Wiederholungsprüfung W2 - 2. Wiederholungsprüfung<br/>
        1,0 - 1,5 sehr gut 1,6 - 2,5 gut 2,6 - 3,5 befriedigend 3,6 - 4,0 ausreichend 4,1 - 5,0 nicht ausreichend"""
        pText6 = Paragraph(text6, style=styles["footnote"])
        textBlock6Story.append(pText6)
        textBlock6.addFromList(textBlock6Story, pdf)

        textBlock7 = Frame(
            0 * cm,
            1 * cm,
            17 * cm,
            1 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        textBlock7Story = []
        text7 = f"""<font fontSize=10>Bescheinigung über Studienleistungen - Seite 2 von 2</font>"""
        pText7 = Paragraph(text7, style=styles["date"])
        textBlock7Story.append(pText7)
        textBlock7.addFromList(textBlock7Story, pdf)

        insertImageFooter(pdf, styles)

        pdf.showPage()

    pdf.save()

    buffer.seek(0)

    return buffer


def createPDF_AnwesenheitVorlesung(user):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.translate(2 * cm, 2 * cm)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer


def createPDF_AnwesenheitPrüfung(user):

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.translate(2 * cm, 2 * cm)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer


def getStyles():

    styles = getSampleStyleSheet()
    headerStyle = ParagraphStyle(
        "header", alignment=TA_LEFT, fontName="Helvetica", fontSize=6.5
    )
    dateStyle = ParagraphStyle(
        "date", alignment=TA_RIGHT, fontName="Helvetica", fontSize=8
    )
    recipientStyle = ParagraphStyle(
        "recipient",
        alignment=TA_LEFT,
        fontName="Helvetica",
        fontSize=11,
        leading=16,
    )
    referenceStyle = ParagraphStyle(
        "reference", alignment=TA_LEFT, fontName="Helvetica", fontSize=14, leading=18
    )
    normalStyle = ParagraphStyle(
        "normal", alignment=TA_LEFT, fontName="Helvetica", fontSize=11, leading=18
    )
    normalSmallStyle = ParagraphStyle(
        "normal_small", alignment=TA_LEFT, fontName="Helvetica", fontSize=8
    )
    normalCenteredStyle = ParagraphStyle(
        "normal_centered",
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=11,
        leading=18,
    )
    tableStyle = ParagraphStyle(
        "table", alignment=TA_LEFT, fontName="Helvetica", fontSize=9, leading=12
    )
    tableCenteredStyle = ParagraphStyle(
        "table_centered",
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=9,
        leading=12,
    )
    disclaimerStyle = ParagraphStyle(
        "disclaimer", alignment=TA_LEFT, fontName="Helvetica", fontSize=8, leading=14
    )
    footnoteStyle = ParagraphStyle(
        "footnote", alignment=TA_LEFT, fontName="Helvetica", fontSize=6, leading=10
    )
    styles.add(headerStyle)
    styles.add(dateStyle)
    styles.add(recipientStyle)
    styles.add(referenceStyle)
    styles.add(normalStyle)
    styles.add(normalSmallStyle)
    styles.add(normalCenteredStyle)
    styles.add(tableStyle)
    styles.add(tableCenteredStyle)
    styles.add(disclaimerStyle)
    styles.add(footnoteStyle)

    return styles


def insertA4Frame(canvas):
    frame = Frame(
        0 * cm,
        0 * cm,
        17 * cm,
        27 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=1,
    )
    story = []
    frame.addFromList(story, canvas)


def insertImageHeader(canvas, styles, showLeftSideLogo=True, showRightSideLogo=False):
    if showLeftSideLogo:
        headerLogo1 = Frame(
            0 * cm,
            24 * cm,
            9 * cm,
            3 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        path = Path(str(settings.BASE_DIR) + "\\static\\media\\ba_leipzig_logo.png")
        w, h = getImage(path, 8.5 * cm)

        headerLogoStory = []
        image = f"""<br/><br/><br/><br/><img src="{path}" width="{w}" height="{h}"/><br/><br/>"""
        pImage = Paragraph(image, style=styles["header"])
        headerLogoStory.append(pImage)
        headerLogo1.addFromList(headerLogoStory, canvas)

    if showRightSideLogo:
        headerLogo2 = Frame(
            11 * cm,
            24 * cm,
            5 * cm,
            3 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        path = Path(
            str(settings.BASE_DIR) + "\\static\\media\\ba_leipzig_motto_logo.png"
        )
        w, h = getImage(path, 5 * cm)

        headerLogo2Story = []
        image2 = f"""<br/><br/><br/><br/><img src="{path}" width="{w}" height="{h}"/><br/><br/>"""
        pImage2 = Paragraph(image2, style=styles["header"])
        headerLogo2Story.append(pImage2)
        headerLogo2.addFromList(headerLogo2Story, canvas)


def insertSenderAndDateHeader(canvas, styles, user):
    sender = Frame(
        0 * cm,
        23 * cm,
        9 * cm,
        1 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    bal = ccm.Institution.objects.filter(
        city=user.seminargroup.course.institution.city
    )[0]

    senderStory = []
    instAddress = f"""{bal.subInstitution} • {bal.streetNameAndNumber} • {bal.zipCode} {bal.city}"""
    pInstAddress = Paragraph(instAddress, style=styles["header"])
    senderStory.append(pInstAddress)
    sender.addFromList(senderStory, canvas)

    dateHeader = Frame(
        12 * cm,
        23 * cm,
        5 * cm,
        1 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    today = dt.date.today().strftime("%d.%m.%Y")
    dateHeaderStory = []
    date = f"{bal.city}, {today}"
    pDate = Paragraph(date, style=styles["date"])
    dateHeaderStory.append(pDate)
    dateHeader.addFromList(dateHeaderStory, canvas)


def insertRecipientHeader(canvas, styles, user):
    recipient = Frame(
        0 * cm,
        20 * cm,
        9 * cm,
        4 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    recipientStory = []

    text = f"""<br/>{getSalutation(user)}<br/>
    {user.first_name} {user.last_name}<br/>
    {user.streetNameAndNumber}<br/>
    {user.zipCode} {user.city}"""
    pText = Paragraph(text, style=styles["recipient"])
    recipientStory.append(pText)
    recipient.addFromList(recipientStory, canvas)


def insertReference(canvas, styles, value):
    reference = Frame(
        0 * cm,
        17.5 * cm,
        17 * cm,
        1.5 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    referenceStory = []
    ref = value
    pRef = Paragraph(ref, style=styles["reference"])
    referenceStory.append(pRef)
    reference.addFromList(referenceStory, canvas)


def insertDisclaimer(canvas, styles, yPosInCM):
    disclaimer = Frame(
        0 * cm,
        yPosInCM * cm,
        17 * cm,
        2 * cm,
        leftPadding=0,
        rightPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )

    disclaimerStory = []
    text = f"""Diese Bescheinigung wurde maschinell erstellt und trägt keine Unterschrift.<br/>
    Änderungen oder zusätzliche Eintragungen sind nur in Verbindung mit Unterschrift und Stempel gültig."""
    pText = Paragraph(text, style=styles["disclaimer"])
    disclaimerStory.append(pText)
    disclaimer.addFromList(disclaimerStory, canvas)


def insertImageFooter(canvas, styles, showLeftSideLogo=True, showRightSideLogo=True):
    if showLeftSideLogo:
        footerLogo1 = Frame(
            0 * cm,
            -1 * cm,
            4 * cm,
            3 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        path = Path(str(settings.BASE_DIR) + "\\static\\media\\ba_leipzig_logo.png")
        w, h = getImage(path, 4 * cm)

        footerLogoStory = []
        image = f"""<br/><br/><br/><br/><img src="{path}" width="{w}" height="{h}"/><br/><br/>"""
        pImage = Paragraph(image, style=styles["header"])
        footerLogoStory.append(pImage)
        footerLogo1.addFromList(footerLogoStory, canvas)

    if showRightSideLogo:
        footerLogo2 = Frame(
            13 * cm,
            -1 * cm,
            3 * cm,
            3 * cm,
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )

        path = Path(
            str(settings.BASE_DIR) + "\\static\\media\\freistaat_sachsen_logo.png"
        )
        w, h = getImage(path, 3 * cm)

        footerLogo2Story = []
        image2 = f"""<br/><br/><br/><br/><img src="{path}" width="{w}" height="{h}"/><br/><br/>"""
        pImage2 = Paragraph(image2, style=styles["header"])
        footerLogo2Story.append(pImage2)
        footerLogo2.addFromList(footerLogo2Story, canvas)


def getSalutation(user):
    if user.gender == "m":
        sal = "Herr"
    elif user.gender == "w":
        sal = "Frau"
    else:
        sal = "Enby"

    return sal


def getImage(path, w=1 * cm):
    img = ImageReader(path)
    iW, iH = img.getSize()
    aspect = iH / float(iW)
    h = w * aspect

    return w, h
