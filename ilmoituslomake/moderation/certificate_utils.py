from base.models import Certificate, CustomerCertificate


def enrich_certificates_data(certificates_data):
    """
    Enrich certificate data by fetching details from the Certificate table.
    
    Input (from frontend):
    [{"id": 1}, {"id": 2}, {"id": -1, "name": {"fi": "Custom"}}]
    
    Output (enriched):
    [
      {
        "id": 1,
        "tyyppi": "Label",
        "name": {"fi": "Joutsenmerkki", "sv": "...", "en": "..."},
        "website": {"fi": "https://...", "sv": "...", "en": "..."}
      },
      ...
    ]
    """
    if not certificates_data:
        return certificates_data
    
    enriched = []
    for cert_data in certificates_data:
        cert_id = cert_data.get('id')
        
        if cert_id is None:
            continue
        
        # For "Other" option, keep custom name from frontend
        if cert_id == -1:
            try:
                other_cert = Certificate.objects.get(pk=-1)
                enriched.append({
                    'id': -1,
                    'tyyppi': cert_data.get('tyyppi', other_cert.certificate_type),
                    'name': cert_data.get('name', {
                        'fi': other_cert.name_fi,
                        'sv': other_cert.name_sv,
                        'en': other_cert.name_en
                    }),
                    'website': {
                        'fi': other_cert.url_fi,
                        'sv': other_cert.url_sv,
                        'en': other_cert.url_en
                    }
                })
            except Certificate.DoesNotExist:
                enriched.append(cert_data)
        else:
            # Fetch complete certificate data from database
            try:
                certificate = Certificate.objects.get(pk=cert_id)
                enriched.append({
                    'id': certificate.id,
                    'tyyppi': certificate.certificate_type,
                    'name': {
                        'fi': certificate.name_fi,
                        'sv': certificate.name_sv,
                        'en': certificate.name_en
                    },
                    'website': {
                        'fi': certificate.url_fi,
                        'sv': certificate.url_sv,
                        'en': certificate.url_en
                    }
                })
            except Certificate.DoesNotExist:
                # Certificate doesn't exist, keep original data
                enriched.append(cert_data)
    
    return enriched

def save_customer_certificates(notification_id, certificates_data):
    """
    Save or update certificates for a notification.
    
    Args:
        notification_id: The ID of the notification (can be Notification or ModeratedNotification)
        certificates_data: Array of certificate objects from the notification data
                          Each object has: id, tyyppi, name (optional for "Other"), website (optional)
    
    The function:
    - Removes existing certificate associations (except when "No label"/"No certificate" is selected)
    - Creates new CustomerCertificate entries based on the certificates array
    - Handles "Other" option (id=-1) with custom names
    - Skips entries where user selected "No label" or "No certificate" (empty selection)
    
    Note: In the database, certificate_id=-1 references the special "Other" Certificate record.
    """
    try:
        # First, delete all existing certificate associations for this notification
        CustomerCertificate.objects.filter(notification_id=notification_id).delete()
        
        # If certificates_data is empty or None, nothing more to do
        if not certificates_data:
            return
        
        # Process each certificate in the array
        for cert_data in certificates_data:
            cert_id = cert_data.get('id')
            cert_type = cert_data.get('tyyppi')  # "Label" or "Certificate"
            
            # Skip if no id provided
            if cert_id is None:
                continue
            
            # Get custom name for "Other" option (id = -1)
            custom_name = None
            if cert_id == -1:
                if 'name' in cert_data and isinstance(cert_data['name'], dict):
                    # Custom name might be in any language field
                    custom_name = (
                        cert_data['name'].get('fi') or 
                        cert_data['name'].get('sv') or 
                        cert_data['name'].get('en')
                    )
                # Only save if custom name provided for "Other"
                if not custom_name:
                    continue
            
            # Look up certificate in Certificate table (including id=-1 for "Other")
            try:
                certificate = Certificate.objects.get(pk=cert_id)
                CustomerCertificate.objects.create(
                    notification_id=notification_id,
                    certificate=certificate,  # ForeignKey stores only the ID in database
                    custom_name=custom_name   # NULL except for "Other" (id=-1)
                )
            except Certificate.DoesNotExist:
                # Certificate ID doesn't exist in master table, skip it
                pass
                    
    except Exception as e:
        # Log error but don't fail the entire notification save
        print(f"Error saving customer certificates: {str(e)}")
        pass
