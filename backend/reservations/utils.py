from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import qrcode
from io import BytesIO
import os
import random
from datetime import datetime, date


def generer_billet_pdf(reservation):
    """Génère un billet PDF premium inspiré des confirmations ONCF"""
    output_dir = os.path.join(settings.MEDIA_ROOT, 'billets')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'billet_{reservation.code_reservation}.pdf')

    primary = colors.HexColor('#f04b23')
    secondary = colors.HexColor('#ff6600')
    grey_light = colors.HexColor('#f7f7f7')
    grey_border = colors.HexColor('#dcdcdc')

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.2*cm,
        bottomMargin=1.2*cm
    )
    story = []
    styles = getSampleStyleSheet()

    # Header - Mise en page améliorée selon l'image
    header_data = [
        [
            Paragraph('<font size=20 color="#f04b23"><b>AGCF</b></font><font size=18 color="#ff6600"><i> Voyages</i></font><br/><font size=10 color="#666666"><i>Votre confirmation e-billet</i></font>',
                      styles['Normal']),
            Paragraph(f'<para alignment=right><font size=11><b>{reservation.date_reservation.strftime("%d/%m/%Y")}</b></font><br/><font size=9>{reservation.date_reservation.strftime("%H:%M")} &nbsp;|&nbsp; {reservation.code_reservation}</font></para>',
                      styles['Normal'])
        ]
    ]
    header_table = Table(header_data, colWidths=[9*cm, 6*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        '<para alignment=center><font size=12 color="#f04b23"><b>VOTRE CONFIRMATION E-BILLET</b></font><br/>'
        '<font size=9 color="#666666">YOUR E-TICKET CONFIRMATION</font></para>',
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))

    # Infos voyageur
    user = reservation.utilisateur
    info_data = [
        ['Nom / Last Name', user.last_name or '—', 'Prénom / First Name', user.first_name or '—'],
        ['Dossier Voyage', reservation.code_reservation, 'Identifiant Client', user.id],
        ['CIN/PP', getattr(user.profil, 'cin', '—') if hasattr(user, 'profil') else '—', 'Transaction', reservation.code_reservation],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey_light),
        ('GRID', (0, 0), (-1, -1), 0.5, grey_border),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4*cm))

    # Générer un numéro de voiture entre 1 et le nombre maximum de voitures du train
    nombre_voitures_max = getattr(reservation.train, 'nombre_voitures', 8) or 8
    numero_voiture = random.randint(1, nombre_voitures_max)
    
    # Résumé trajet - Mise en page améliorée selon l'image
    travel_summary = Table([
        ['ALLER / DEPARTURE', reservation.date_voyage.strftime('%d/%m/%Y'), 'Montant / Price', f"{reservation.prix_total:.2f} DH"],
        [f"{reservation.train.gare_depart.nom} ({reservation.train.gare_depart.ville}) → "
         f"{reservation.train.gare_arrivee.nom} ({reservation.train.gare_arrivee.ville})",
         '', 'Classe', reservation.train.get_classe_display()],
        ['Voiture / Car', f"N° {numero_voiture}", 'Places / Seats', f"{reservation.nombre_places}"],
    ], colWidths=[5.5*cm, 4.5*cm, 3.5*cm, 4.5*cm])
    travel_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.7, grey_border),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('FONTSIZE', (0, 2), (-1, 2), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(travel_summary)
    story.append(Spacer(1, 0.4*cm))

    # QR + détails
    qr = qrcode.QRCode(version=2, box_size=8, border=2)
    qr.add_data(f"AGCF:{reservation.code_reservation}:{reservation.train.numero}:{reservation.date_voyage}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=5*cm, height=5*cm)

    qr_table = Table([
        [qr_image, Paragraph(
            f"<b>N° e-billet:</b> {reservation.code_reservation}<br/>"
            f"<b>Train:</b> {reservation.train.numero}<br/>"
            f"<b>Voiture:</b> {numero_voiture}<br/>"
            f"<b>Nombre de places:</b> {reservation.nombre_places}<br/>"
            f"<b>Durée:</b> {reservation.train.duree_formatee}<br/><br/>"
            f"<b>Départ:</b> {reservation.train.gare_depart.nom} à {reservation.train.heure_depart.strftime('%H:%M')}<br/>"
            f"<b>Arrivée:</b> {reservation.train.gare_arrivee.nom} à {reservation.train.heure_arrivee.strftime('%H:%M')}<br/>",
            styles['Normal']
        )]
    ], colWidths=[5*cm, 10*cm])
    qr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.8, grey_border),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
        ('RIGHTPADDING', (1, 0), (1, 0), 10),
    ]))
    story.append(qr_table)
    story.append(Spacer(1, 0.4*cm))

    # Passagers avec numéros de place
    # Générer des numéros de place entre 1 et le nombre maximum de places dans le train
    # On suppose qu'une voiture a environ 50 places, donc on limite à 50 par voiture
    places_par_voiture = 50
    passagers_data = [['Nom / Name', 'Prénom / First name', 'Date de naissance', 'Place / Seat']]
    place_num = 1
    for passager in reservation.passagers.all():
        # Générer un numéro de place valide (entre 1 et places_par_voiture)
        num_place = min(place_num, places_par_voiture)
        passagers_data.append([
            passager.nom,
            passager.prenom,
            passager.date_naissance.strftime('%d/%m/%Y'),
            f"{numero_voiture}-{num_place:02d}"
        ])
        place_num += 1
    
    # Si pas de passagers, afficher le nombre de places réservées
    if not reservation.passagers.exists():
        for i in range(reservation.nombre_places):
            # Générer un numéro de place valide (entre 1 et places_par_voiture)
            num_place = min(i + 1, places_par_voiture)
            passagers_data.append([
                reservation.utilisateur.last_name or '—',
                reservation.utilisateur.first_name or '—',
                '—',
                f"{numero_voiture}-{num_place:02d}"
            ])
    
    passager_table = Table(passagers_data, colWidths=[4.5*cm, 4.5*cm, 3.5*cm, 3.5*cm])
    passager_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey_light),
        ('GRID', (0, 0), (-1, -1), 0.6, grey_border),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(passager_table)
    story.append(Spacer(1, 0.4*cm))

    # Conditions
    conditions_text = (
        "<b>Conditions d'utilisation | Politique de confidentialité</b><br/>"
        "Ce e-billet est nominatif et doit être présenté avec une pièce d'identité. "
        "Les échanges/annulations suivent les conditions AGCF Voyages (Flex jusqu'à 30 min après départ).<br/>"
        "Service client : +212 699-634998 • support@agcf-voyages.com • www.agcf-voyages.ma"
    )
    conditions_box = Table([[Paragraph(conditions_text, styles['Normal'])]])
    conditions_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 0.6, grey_border),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(conditions_box)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        '<para alignment=center><font size=9 color="#999999">© '
        f'{date.today().year} AGCF Voyages · www.agcf-voyages.ma</font></para>',
        styles['Normal']
    ))

    doc.build(story)
    return pdf_path


def envoyer_billet_email(reservation, pdf_path, est_modification=False):
    """Envoie le billet par email avec un template HTML premium"""
    utilisateur = reservation.utilisateur
    depart_ville = reservation.train.gare_depart.ville
    arrivee_ville = reservation.train.gare_arrivee.ville
    date_voyage_str = reservation.date_voyage.strftime('%d/%m/%Y')
    heure_depart = reservation.train.heure_depart.strftime('%H:%M')
    heure_arrivee = reservation.train.heure_arrivee.strftime('%H:%M')

    html_body = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .container {{
            max-width: 640px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 15px 45px rgba(0,0,0,0.08);
        }}
        .header {{
            background: linear-gradient(135deg, #ff4d00, #ff6600);
            color: #fff;
            padding: 32px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            letter-spacing: 1px;
        }}
        .header span {{
            display: block;
            margin-top: 6px;
            font-size: 14px;
            opacity: 0.8;
        }}
        .section {{
            padding: 28px 32px;
        }}
        .section h2 {{
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #ff6600;
            margin-bottom: 12px;
        }}
        .summary-card {{
            background-color: #fdf2ec;
            border: 1px solid #ffd7c2;
            border-radius: 12px;
            padding: 16px 20px;
        }}
        .summary-card strong {{
            font-size: 18px;
            color: #e65100;
        }}
        .summary-card p {{
            margin: 4px 0;
        }}
        .details-list {{
            list-style: none;
            padding: 0;
            margin: 18px 0 0;
        }}
        .details-list li {{
            margin-bottom: 8px;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            background-color: #eef1ff;
            color: #2c3e50;
            font-size: 13px;
            margin-right: 8px;
        }}
        .footer {{
            background-color: #111;
            color: #fff;
            padding: 18px 32px;
            font-size: 13px;
            text-align: center;
        }}
        .footer a {{
            color: #ff8a3c;
            text-decoration: none;
        }}
        .footer small {{
            display: block;
            margin-top: 8px;
            opacity: 0.7;
        }}
        .cta {{
            margin-top: 20px;
            text-align: center;
        }}
        .cta a {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #ff6600;
            color: #fff !important;
            padding: 12px 24px;
            border-radius: 999px;
            text-decoration: none;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(255, 102, 0, 0.25);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{'Votre billet modifié' if est_modification else 'Votre récapitulatif'}</h1>
            <span>Voyage du {date_voyage_str}</span>
        </div>

        <div class="section">
            <h2>{depart_ville.upper()} → {arrivee_ville.upper()}</h2>
            <div class="summary-card">
                <strong>Bonjour {utilisateur.first_name or utilisateur.username},</strong>
                <p>{'Votre réservation a été modifiée avec succès. Voici votre nouveau billet pour le trajet du' if est_modification else 'Nous confirmons la réservation de votre trajet du'} {date_voyage_str} à {heure_depart}.</p>
                <ul class="details-list">
                    <li><span class="tag">N° e-billet</span> {reservation.code_reservation}</li>
                    <li><span class="tag">Train</span> {reservation.train.numero} • {reservation.train.get_classe_display()}</li>
                    <li><span class="tag">Trajet</span> {depart_ville} ({reservation.train.gare_depart.nom}) → {arrivee_ville} ({reservation.train.gare_arrivee.nom})</li>
                    <li><span class="tag">Horaires</span> Départ {heure_depart} • Arrivée {heure_arrivee}</li>
                    <li><span class="tag">Voiture</span> N° {random.randint(1, getattr(reservation.train, 'nombre_voitures', 8) or 8)}</li>
                    <li><span class="tag">Places</span> {reservation.nombre_places} place(s)</li>
                    <li><span class="tag">Montant</span> {reservation.prix_total:.2f} DH</li>
                </ul>
            </div>

            <div class="cta">
                <a href="#" style="pointer-events:none;">Billet PDF en pièce jointe</a>
            </div>
        </div>

        <div class="section" style="border-top:1px solid #f0f0f0;">
            <h2>Conditions d'utilisation</h2>
            <p style="font-size:13px; line-height:1.6; color:#555;">
                Ce billet est nominatif et doit être présenté lors des contrôles accompagné d'une pièce d'identité en cours de validité. <br>
                Les échanges et annulations sont possibles conformément aux conditions AGCF Voyages. <br>
                Pour toute question, contactez notre centre d'aide au +212 699-634998 ou via support@agcf-voyages.com.
            </p>
        </div>

        <div class="footer">
            L'équipe AGCF Voyages<br>
            <a href="https://agcf-voyages.ma">www.agcf-voyages.ma</a>
            <small>© {date.today().year} AGCF Voyages. Tous droits réservés.</small>
        </div>
    </div>
</body>
</html>
    """

    sujet = f'{"Votre billet modifié" if est_modification else "Votre billet"} AGCF Voyages - {depart_ville} → {arrivee_ville}'
    email = EmailMessage(
        subject=sujet,
        body=html_body,
        from_email=settings.EMAIL_HOST_USER or 'noreply@agcf-voyages.com',
        to=[reservation.utilisateur.email],
    )
    email.content_subtype = 'html'

    # Attacher le PDF
    with open(pdf_path, 'rb') as pdf:
        email.attach(f'billet_{reservation.code_reservation}.pdf', pdf.read(), 'application/pdf')
    
    email.send()


def envoyer_notif_retard(retard, reservations):
    """Avertit automatiquement les voyageurs concernés par un retard"""
    if not reservations:
        return
    expediteur = settings.EMAIL_HOST_USER or 'noreply@agcf-voyages.com'
    motif = retard.motif.strip() if retard.motif else "Motif non communiqué"

    for reservation in reservations:
        destinataire = reservation.utilisateur.email
        if not destinataire:
            continue

        sujet = f"[AGCF Voyages] Retard annoncé pour votre train {retard.train.numero}"
        message = f"""
Bonjour {reservation.utilisateur.get_full_name() or reservation.utilisateur.username},

Votre train {retard.train.numero} reliant {retard.train.gare_depart.ville} à {retard.train.gare_arrivee.ville}
prévu le {retard.date_voyage.strftime('%d/%m/%Y')} accuse actuellement un retard estimé à {retard.minutes_retard} minute(s).

Statut du suivi : {retard.get_statut_display()}
Motif : {motif}

Nous vous invitons à vérifier régulièrement votre espace AGCF Voyages pour suivre l'évolution de votre trajet.

Merci pour votre compréhension,
L'équipe AGCF Voyages
""".strip()

        send_mail(
            sujet,
            message,
            expediteur,
            [destinataire],
            fail_silently=True,
        )

