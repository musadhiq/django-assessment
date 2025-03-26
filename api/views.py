import csv
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from userManagement.models import User
from .serializers import UserSerializer


@api_view(["GET"])
def index(request):
    return Response({"hello": "world"})


@api_view(["GET"])
def get_users(request):
    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data)


@api_view(["POST"])
def import_users(request):
    file = request.FILES.get("file")
    if not file or not file.name.endswith(".csv"):
        return Response({"message": "Only .csv file is accepted"}, status=400)

    users_to_create = []
    errors = []

    try:
        reader = csv.DictReader(file.read().decode("utf-8").splitlines())
        existing_emails = set(User.objects.values_list("email", flat=True))

        for row in reader:
            name, email, age = row.get("name"), row.get("email"), row.get("age")

            if not name or not email or not age:
                errors.append({"data": row, "message": "Missing required fields"})
                continue

            try:
                # validate email using django validators 
                validate_email(email)
                age = int(age)
                if age < 0 or age > 120:
                    raise ValueError("Age must be between 0 and 120")
            except (ValidationError, ValueError) as e:
                errors.append({"data": row, "message": str(e)})
                continue

            if email in existing_emails or any(user.email == email for user in users_to_create):
                errors.append({"data": row, "message": "User already exists"})
            else:
                users_to_create.append(User(name=name, email=email, age=age))

        # Bulk create users at last
        if users_to_create:
            User.objects.bulk_create(users_to_create)

    except Exception as e:
        return Response(
            {"message": "Error processing file", "error": str(e)}, status=500
        )
    
    serialized_users = UserSerializer(users_to_create, many=True).data
    

    response = Response(
        {
            "success": serialized_users,
            "rejected": errors,
            "successCount": len(users_to_create),
            "rejectedCount": len(errors),
        }
    )

    return response
