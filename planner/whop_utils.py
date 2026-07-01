import requests
from django.conf import settings

WHOP_API_BASE = 'https://api.whop.com/api/v1'

def get_headers():
    return {
        'Authorization': f'Bearer {settings.WHOP_API_KEY}',
        'Content-Type': 'application/json',
    }

def create_checkout_session(user, affiliate_id=None):
    """Skapa en Whop checkout-session för en användare"""
    payload = {
        'plan_id': settings.WHOP_PLAN_ID,
        'customer': {
            'email': user.email or '',
            'external_id': str(user.id),
        },
        'metadata': {
            'user_id': user.id,
            'username': user.username,
        },
    }
    
    if affiliate_id:
        payload['affiliate_id'] = affiliate_id
    
    try:
        response = requests.post(
            f'{WHOP_API_BASE}/payment_links',
            json=payload,
            headers=get_headers(),
            timeout=10
    )

        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return {
                'success': True,
                'checkout_url': data.get('checkout_url'),
                'session_id': data.get('id'),
            }
        else:
            print(f"❌ Whop checkout error: {response.status_code} - {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"❌ Whop API error: {e}")
        return {'success': False, 'error': str(e)}


def get_memberships(email=None, affiliate_id=None):
    """Hämta alla medlemskap/prenumerationer"""
    params = {}
    if email:
        params['email'] = email
    if affiliate_id:
        params['affiliate_id'] = affiliate_id
    
    try:
        response = requests.get(
            f'{WHOP_API_BASE}/memberships',
            params=params,
            headers=get_headers(),
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Whop API error: {e}")
        return None


def get_affiliate_earnings(affiliate_id):
    """Hämta en affiliates förtjänster"""
    try:
        response = requests.get(
            f'{WHOP_API_BASE}/affiliates/{affiliate_id}/earnings',
            headers=get_headers(),
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Whop API error: {e}")
        return None

def create_affiliate(email, name=None):
    """Skapa en ny affiliate i Whop-programmet"""
    payload = {
        'plan_id': settings.WHOP_PLAN_ID,
        'email': email,
    }
    if name:
        payload['name'] = name
    
    try:
        response = requests.post(
            f'{WHOP_API_BASE}/affiliates',
            json=payload,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return {
                'success': True,
                'affiliate_id': data.get('id'),
                'affiliate_link': data.get('referral_link'),
            }
        else:
            print(f"❌ Skapa affiliate error: {response.text}")
            return {'success': False}
    except Exception as e:
        print(f"❌ API error: {e}")
        return {'success': False}


def get_affiliate_info(affiliate_id):
    """Hämta info om en affiliate"""
    try:
        response = requests.get(
            f'{WHOP_API_BASE}/affiliates/{affiliate_id}',
            headers=get_headers(),
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ API error: {e}")
        return None


def get_or_create_affiliate(email, name=None):
    """Hämta befintlig affiliate eller skapa ny"""
    # Försök hitta först (Whop har tyvärr ingen "list affiliates" endpoint)
    # Så vi skapar en ny - Whop deduplicerar på email
    result = create_affiliate(email, name)
    return result


def get_affiliate_stats(affiliate_id):
    """Hämta statistik för en affiliate"""
    try:
        # Hämta intäkter
        earnings_response = requests.get(
            f'{WHOP_API_BASE}/affiliates/{affiliate_id}/earnings',
            headers=get_headers(),
            timeout=10
        )
        earnings = earnings_response.json() if earnings_response.status_code == 200 else None
        
        # Hämta antal klick/konverteringar
        stats_response = requests.get(
            f'{WHOP_API_BASE}/affiliates/{affiliate_id}/stats',
            headers=get_headers(),
            timeout=10
        )
        stats = stats_response.json() if stats_response.status_code == 200 else None
        
        return {
            'success': True,
            'earnings': earnings,
            'stats': stats,
        }
    except Exception as e:
        print(f"❌ API error: {e}")
        return {'success': False}