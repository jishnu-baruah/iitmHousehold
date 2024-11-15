from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.customer import bp
from app.models.service import Service
from app.models.request import ServiceRequest
from app.models.user import Professional
from app.forms.search import SearchForm
from app.forms.request import ServiceRequestForm, ReviewForm
from app import db
from datetime import datetime
from sqlalchemy import or_, and_

@bp.route('/search', methods=['GET'])
@login_required
def search_services():
    if current_user.role != "customer":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    form = SearchForm()
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    pincode = request.args.get('pincode', '')
    service_type = request.args.get('service_type', '')
    price_range = request.args.get('price_range', '')

    # Base query for active services
    services = Service.query.filter_by(is_active=True)

    # Apply search query filter
    if query:
        services = services.filter(
            or_(
                Service.name.ilike(f'%{query}%'),
                Service.description.ilike(f'%{query}%')
            )
        )

    # Apply service type filter
    if service_type:
        services = services.filter(Service.service_type == service_type)

    # Apply price range filter
    if price_range:
        price_ranges = {
            '0-50': (0, 50),
            '50-100': (50, 100),
            '100-200': (100, 200),
            '200+': (200, float('inf'))
        }
        if price_range in price_ranges:
            min_price, max_price = price_ranges[price_range]
            services = services.filter(
                Service.base_price >= min_price
            ) if max_price == float('inf') else services.filter(
                and_(
                    Service.base_price >= min_price,
                    Service.base_price <= max_price
                )
            )

    # Get professionals for location filtering
    if location or pincode:
        professionals = Professional.query.filter(
            and_(
                Professional.is_verified == True,
                Professional.is_available == True,
                or_(
                    Professional.location.ilike(f'%{location}%') if location else False,
                    Professional.pincode == pincode if pincode else False
                )
            )
        ).all()
        
        professional_services = {prof.service_type for prof in professionals if prof.service_type}
        services = services.filter(Service.service_type.in_(professional_services))

    services = services.all()

    # Get available professionals for each service
    service_data = []
    for service in services:
        available_professionals = Professional.query.filter_by(
            service_type=service.service_type,
            is_verified=True,
            is_available=True
        )

        if location:
            available_professionals = available_professionals.filter(
                Professional.location.ilike(f'%{location}%')
            )
        
        if pincode:
            available_professionals = available_professionals.filter(
                Professional.pincode == pincode
            )
        
        prof_count = available_professionals.count()
        service_data.append({
            'service': service,
            'professional_count': prof_count
        })

    return render_template('customer/search.html', 
                           form=form,
                           service_data=service_data,
                           search_params={
                               'query': query,
                               'location': location,
                               'pincode': pincode,
                               'service_type': service_type,
                               'price_range': price_range
                           })

@bp.route('/search/suggestions')
@login_required
def search_suggestions():
    query = request.args.get('query', '')
    if len(query) < 2:
        return jsonify([])
    
    suggestions = Service.query.filter(
        and_(
            Service.is_active == True,
            or_(
                Service.name.ilike(f'%{query}%'),
                Service.description.ilike(f'%{query}%')
            )
        )
    ).limit(5).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description[:100] + '...' if len(s.description) > 100 else s.description
    } for s in suggestions])
