"""Main app views."""
from . import main
from .forms import BookingForm
from .. import db
from ..models import Booking, Desk
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_paginate import Pagination


@main.route('/')
def index():
    """Index route."""
    return render_template('index.html')


@main.route('/book', methods=['GET', 'POST'])
def book():
    """Desk booking route."""
    form = BookingForm()
    if form.validate_on_submit():
        # Determine the begining and end of the booking as datetime objects
        date = form.date.data
        from_when = datetime.combine(date, form.from_when.data.time())
        until_when = datetime.combine(date, form.until_when.data.time())

        # Create a Booking objet
        booking = Booking(
            name=form.name.data,
            desk_id=form.desk.data,
            from_when=from_when,
            until_when=until_when,
        )
        # Ensure the booking does not overlap with existing bookings
        bookings = Booking.query.filter_by(desk_id=form.desk.data).all()
        if any((booking.overlap(other) for other in bookings)):
            flash("Your request overlaps with an existing booking.")
            return render_template('book.html', form=form)

        # Ensure the booking ends after it begins
        if booking.from_when > booking.until_when:
            flash("Your request ends after it begins.")
            return render_template('book.html', form=form)

        # Ensure the booking is not for zero time
        if booking.from_when == booking.until_when:
            flash("Your request is for zero time.")
            return render_template('book.html', form=form)

        db.session.add(booking)
        db.session.commit()
        flash('Your desk is booked!')
        return redirect(url_for('main.bookings'))
    return render_template('book.html', form=form)


@main.route('/bookings')
def bookings():
    """Route to show all bookings."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PER_PAGE']
    bookings = Booking.query.paginate(page, per_page, False).items
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=len(Booking.query.all()),
        css_framework='bootstrap3',
    )
    return render_template(
        'bookings.html', bookings=bookings, per_page=per_page, pagination=pagination
    )


@main.route('/desks')
def desks():
    """Route to show all desks and their current status."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PER_PAGE']
    desks = Desk.query.paginate(page, per_page, False).items
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=len(Desk.query.all()),
        css_framework='bootstrap3',
    )
    return render_template(
        'desks.html', desks=desks, per_page=per_page, pagination=pagination
    )