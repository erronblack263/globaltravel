from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date
from typing import Optional
import qrcode
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import uuid

from models.ticket import Ticket
from models.booking import Booking
from models.payment import Payment
from core.config import settings


class TicketService:
    """Service for generating and managing tickets."""
    
    @staticmethod
    async def generate_ticket_number() -> str:
        """Generate unique ticket number."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = str(uuid.uuid4())[:8].upper()
        return f"GT-{timestamp}-{random_part}"
    
    @staticmethod
    def generate_qr_code(ticket_data: dict) -> str:
        """Generate QR code for ticket."""
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add ticket data to QR code
        qr_data = f"Ticket ID: {ticket_data['ticket_number']}\n"
        qr_data += f"Booking ID: {ticket_data['booking_id']}\n"
        qr_data += f"User ID: {ticket_data['user_id']}\n"
        qr_data += f"Valid From: {ticket_data['valid_from']}\n"
        qr_data += f"Valid Until: {ticket_data['valid_until']}"
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def generate_pdf_ticket(ticket_data: dict, booking_data: dict) -> bytes:
        """Generate PDF ticket."""
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, height - 50, "GLOBAL TRAVEL TICKET")
        
        # Ticket number
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 100, f"Ticket Number: {ticket_data['ticket_number']}")
        
        # Booking details
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 140, "Booking Details:")
        
        p.setFont("Helvetica", 12)
        y_position = height - 160
        
        if booking_data['booking_type'] == 'resort':
            p.drawString(70, y_position, f"Resort: {booking_data['resort_name']}")
            y_position -= 20
            p.drawString(70, y_position, f"Address: {booking_data['resort_address']}")
            y_position -= 20
            p.drawString(70, y_position, f"Check-in: {booking_data['check_in_date']}")
            y_position -= 20
            p.drawString(70, y_position, f"Check-out: {booking_data['check_out_date']}")
        else:
            p.drawString(70, y_position, f"Destination: {booking_data['destination_name']}")
            y_position -= 20
            p.drawString(70, y_position, f"Address: {booking_data['destination_address']}")
            y_position -= 20
            p.drawString(70, y_position, f"Visit Date: {booking_data['check_in_date']}")
        
        y_position -= 20
        p.drawString(70, y_position, f"Number of Guests: {booking_data['number_of_guests']}")
        y_position -= 20
        p.drawString(70, y_position, f"Total Amount: ${booking_data['total_amount']}")
        
        # Validity period
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position - 40, "Validity Period:")
        
        p.setFont("Helvetica", 12)
        p.drawString(70, y_position - 60, f"Valid From: {ticket_data['valid_from']}")
        p.drawString(70, y_position - 80, f"Valid Until: {ticket_data['valid_until']}")
        
        # Add QR code if available
        if ticket_data.get('qr_code'):
            # This would require more complex implementation to add image to PDF
            # For now, just add a placeholder
            p.setFont("Helvetica", 10)
            p.drawString(50, 100, "QR Code: [Embedded]")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(50, 50, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        p.drawString(50, 35, f"{settings.APP_NAME} - {settings.VERSION}")
        
        p.save()
        buffer.seek(0)
        
        return buffer.getvalue()
    
    @staticmethod
    async def create_ticket(
        booking_id: int,
        payment_id: int,
        user_id: int,
        db: AsyncSession
    ) -> Ticket:
        """Create a new ticket for a confirmed booking."""
        
        # Get booking details
        booking_stmt = select(Booking).where(Booking.id == booking_id)
        booking_result = await db.execute(booking_stmt)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Get payment details
        payment_stmt = select(Payment).where(Payment.id == payment_id)
        payment_result = await db.execute(payment_stmt)
        payment = payment_result.scalar_one_or_none()
        
        if not payment:
            raise ValueError("Payment not found")
        
        # Generate ticket number
        ticket_number = await TicketService.generate_ticket_number()
        
        # Determine validity period
        valid_from = booking.check_in_date
        if booking.booking_type == 'resort':
            valid_until = booking.check_out_date
        else:
            # For destinations, valid for the visit date
            valid_until = booking.check_in_date
        
        # Create ticket data for QR code
        ticket_data = {
            'ticket_number': ticket_number,
            'booking_id': booking_id,
            'user_id': user_id,
            'valid_from': valid_from,
            'valid_until': valid_until
        }
        
        # Generate QR code
        qr_code = TicketService.generate_qr_code(ticket_data)
        
        # Create ticket record
        db_ticket = Ticket(
            ticket_number=ticket_number,
            booking_id=booking_id,
            user_id=user_id,
            payment_id=payment_id,
            qr_code=qr_code,
            valid_from=valid_from,
            valid_until=valid_until,
            status='active'
        )
        
        db.add(db_ticket)
        await db.commit()
        await db.refresh(db_ticket)
        
        return db_ticket
    
    @staticmethod
    async def generate_ticket_pdf(
        ticket_id: int,
        db: AsyncSession
    ) -> bytes:
        """Generate PDF for existing ticket."""
        
        # Get ticket details
        ticket_stmt = select(Ticket).where(Ticket.id == ticket_id)
        ticket_result = await db.execute(ticket_stmt)
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Get booking details
        booking_stmt = select(Booking).where(Booking.id == ticket.booking_id)
        booking_result = await db.execute(booking_stmt)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Prepare ticket data
        ticket_data = {
            'ticket_number': ticket.ticket_number,
            'valid_from': ticket.valid_from,
            'valid_until': ticket.valid_until,
            'qr_code': ticket.qr_code
        }
        
        # Prepare booking data
        booking_data = {
            'booking_type': booking.booking_type,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'number_of_guests': booking.number_of_guests,
            'total_amount': float(booking.total_amount),
            'resort_name': getattr(booking.resort, 'name', None) if booking.resort else None,
            'resort_address': getattr(booking.resort, 'address', None) if booking.resort else None,
            'destination_name': getattr(booking.destination, 'name', None) if booking.destination else None,
            'destination_address': getattr(booking.destination, 'address', None) if booking.destination else None,
        }
        
        # Generate PDF
        pdf_bytes = TicketService.generate_pdf_ticket(ticket_data, booking_data)
        
        # Update ticket with PDF URL (in production, this would be uploaded to S3)
        ticket.pdf_url = f"tickets/{ticket.ticket_number}.pdf"
        await db.commit()
        
        return pdf_bytes
    
    @staticmethod
    async def validate_ticket(
        ticket_number: str,
        db: AsyncSession
    ) -> Optional[Ticket]:
        """Validate ticket by number."""
        
        stmt = select(Ticket).where(
            Ticket.ticket_number == ticket_number
        )
        result = await db.execute(stmt)
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            return None
        
        # Check if ticket is active and valid
        today = date.today()
        if (ticket.status != 'active' or 
            today < ticket.valid_from or 
            today > ticket.valid_until):
            return None
        
        return ticket
