from django.conf import settings
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import qrcode
from io import BytesIO
import os
from datetime import datetime


def generer_billet_pdf(reservation):
    """Génère un billet PDF pour une réservation"""
    # Créer le répertoire de sortie si nécessaire
    output_dir = os.path.join(settings.MEDIA_ROOT, 'billets')
    os.makedirs(output_dir, exist_ok=True)
    
    # Chemin du fichier PDF
    pdf_path = os.path.join(output_dir, f'billet_{reservation.code_reservation}.pdf')
    
    # Créer le document PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Titre
    story.append(Paragraph("AGCF VOYAGES", title_style))
    story.append(Paragraph("Billet de Train Électronique", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Code QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"RESERVATION:{reservation.code_reservation}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Sauvegarder le QR code temporairement
    qr_buffer = BytesIO()
    img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=4*cm, height=4*cm)
    story.append(qr_image)
    story.append(Spacer(1, 0.5*cm))
    
    # Informations de la réservation
    data = [
        ['Code de réservation:', reservation.code_reservation],
        ['Date de réservation:', reservation.date_reservation.strftime('%d/%m/%Y %H:%M')],
        ['Statut:', reservation.get_statut_display()],
    ]
    
    table = Table(data, colWidths=[5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    
    # Informations du train
    story.append(Paragraph("Informations du Train", heading_style))
    train_data = [
        ['Numéro de train:', reservation.train.numero],
        ['Gare de départ:', f"{reservation.train.gare_depart.nom} ({reservation.train.gare_depart.ville})"],
        ['Gare d\'arrivée:', f"{reservation.train.gare_arrivee.nom} ({reservation.train.gare_arrivee.ville})"],
        ['Date de voyage:', reservation.date_voyage.strftime('%d/%m/%Y')],
        ['Heure de départ:', reservation.train.heure_depart.strftime('%H:%M')],
        ['Heure d\'arrivée:', reservation.train.heure_arrivee.strftime('%H:%M')],
        ['Durée:', reservation.train.duree_formatee],
        ['Classe:', reservation.train.get_classe_display()],
    ]
    
    train_table = Table(train_data, colWidths=[5*cm, 10*cm])
    train_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(train_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Informations des passagers
    story.append(Paragraph("Passagers", heading_style))
    passagers_data = [['Nom', 'Prénom', 'Date de naissance']]
    for passager in reservation.passagers.all():
        passagers_data.append([
            passager.nom,
            passager.prenom,
            passager.date_naissance.strftime('%d/%m/%Y')
        ])
    
    passagers_table = Table(passagers_data, colWidths=[5*cm, 5*cm, 5*cm])
    passagers_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(passagers_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Informations de paiement
    story.append(Paragraph("Informations de Paiement", heading_style))
    paiement_data = [
        ['Nombre de places:', str(reservation.nombre_places)],
        ['Prix unitaire:', f"{reservation.prix_unitaire:.2f} DH"],
    ]
    
    if reservation.carte_reduction:
        paiement_data.append(['Carte de réduction:', reservation.carte_reduction.carte.nom])
        paiement_data.append(['Réduction appliquée:', f"-{reservation.reduction_appliquee:.2f} DH"])
    
    paiement_data.append(['Prix total:', f"{reservation.prix_total:.2f} DH"])
    paiement_data.append(['Mode de paiement:', reservation.get_mode_paiement_display() if reservation.mode_paiement else 'N/A'])
    
    paiement_table = Table(paiement_data, colWidths=[5*cm, 10*cm])
    paiement_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (-1, -2), (-1, -1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (-1, -2), (-1, -1), colors.white),
        ('FONTNAME', (-1, -2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-1, -2), (-1, -1), 12),
    ]))
    story.append(paiement_table)
    story.append(Spacer(1, 1*cm))
    
    # Note importante
    story.append(Paragraph(
        "<b>Note importante:</b> Présentez ce billet électronique (ou le code QR) lors de l'embarquement. "
        "Assurez-vous d'arriver à la gare au moins 15 minutes avant le départ.",
        normal_style
    ))
    
    # Construire le PDF
    doc.build(story)
    
    return pdf_path


def envoyer_billet_email(reservation, pdf_path):
    """Envoie le billet par email"""
    email = EmailMessage(
        subject=f'Votre billet de train - Réservation {reservation.code_reservation}',
        body=f"""
Bonjour {reservation.utilisateur.get_full_name() or reservation.utilisateur.username},

Votre réservation a été confirmée avec succès !

Code de réservation: {reservation.code_reservation}
Train: {reservation.train.numero}
Date: {reservation.date_voyage.strftime('%d/%m/%Y')}
Départ: {reservation.train.gare_depart.ville} à {reservation.train.heure_depart.strftime('%H:%M')}
Arrivée: {reservation.train.gare_arrivee.ville} à {reservation.train.heure_arrivee.strftime('%H:%M')}
Prix total: {reservation.prix_total:.2f} DH

Votre billet électronique est joint à cet email. Vous pouvez également le télécharger depuis votre espace personnel.

Merci de votre confiance,
L'équipe AGCF Voyages
        """,
        from_email=settings.EMAIL_HOST_USER or 'noreply@agcf-voyages.com',
        to=[reservation.utilisateur.email],
    )
    
    # Attacher le PDF
    with open(pdf_path, 'rb') as pdf:
        email.attach(f'billet_{reservation.code_reservation}.pdf', pdf.read(), 'application/pdf')
    
    email.send()

