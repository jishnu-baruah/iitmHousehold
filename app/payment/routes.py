from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.payment import bp
from app.models.payment import Payment, Invoice
from app.forms.payment import PaymentForm, UPIPaymentForm, RefundForm
from app.models.request import ServiceRequest
from app import db
from datetime import datetime
import json

@bp.route('/process/<int:request_id>', methods=['GET', 'POST'])
@login_required
def process_payment(request_id):
    if current_user.role != "customer":
        flash("Access denied", "danger")
        return redirect(url_for('main.index'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.customer_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('customer.dashboard'))
    
    form = PaymentForm() if request.args.get('method') != 'upi' else UPIPaymentForm()
    
    if form.validate_on_submit():
        payment = Payment(
            request_id=request_id,
            customer_id=current_user.id,
            professional_id=service_request.professional_id,
            amount=service_request.service.base_price,
            payment_method=form.payment_method.data if hasattr(form, 'payment_method') else 'upi'
        )
        
        # Process payment
        payment_details = {
            'method': payment.payment_method,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'form_data': {field.name: field.data for field in form if field.name != 'submit'}
        }
        
        success, message = payment.process_payment(payment_details)
        
        if success:
            flash("Payment processed successfully!", "success")
            return redirect(url_for('payment.invoice', payment_id=payment.id))
        else:
            flash(f"Payment failed: {message}", "danger")
            return redirect(url_for('payment.process', request_id=request_id))
    
    return render_template('payment/process.html', 
                         form=form, 
                         service_request=service_request)

@bp.route('/invoice/<int:payment_id>')
@login_required
def invoice(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == "customer" and payment.customer_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('customer.dashboard'))
    
    if current_user.role == "professional" and payment.professional_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('professional.dashboard'))
    
    invoice_data = payment.generate_invoice()
    return render_template('payment/invoice.html', 
                         payment=payment,
                         invoice_data=invoice_data)

@bp.route('/refund/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def refund(payment_id):
    if current_user.role != "admin":
        flash("Access denied", "danger")
        return redirect(url_for('main.index'))
    
    payment = Payment.query.get_or_404(payment_id)
    form = RefundForm()
    
    if form.validate_on_submit():
        payment.status = "refunded"
        # Create refund record and update balances
        # This would integrate with actual payment gateway in production
        
        db.session.commit()
        flash("Refund processed successfully", "success")
        return redirect(url_for('admin.dashboard'))
    
    return render_template('payment/refund.html', 
                         form=form, 
                         payment=payment)

@bp.route('/payment-history')
@login_required
def payment_history():
    if current_user.role == "customer":
        payments = Payment.query.filter_by(customer_id=current_user.id).all()
    elif current_user.role == "professional":
        payments = Payment.query.filter_by(professional_id=current_user.id).all()
    else:
        payments = Payment.query.all()
    
    return render_template('payment/history.html', payments=payments)

@bp.route('/download-invoice/<int:payment_id>')
@login_required
def download_invoice(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if current_user.role == "customer" and payment.customer_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('customer.dashboard'))
    
    # Generate PDF invoice
    invoice_data = payment.generate_invoice()
    # Here you would generate a PDF using a library like reportlab or WeasyPrint
    # For now, we'll just return the data
    return jsonify(invoice_data)
