alias build-ticketverkauf-dev="docker build -t TicketverkaufHSG25 ."
alias run-ticketverkauf-dev="docker run -d -p 80:80 --name ticketverkauf-dev TicketverkaufHSG25"
alias stop-ticketverkauf-dev="docker stop ticketverkauf-dev"
