from django.db.models import Avg, Count
from rest_framework import permissions, status
from rest_framework.viewsets import ViewSet

from apps.permissions import IsEmailVerified
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewReadSerializer, ReviewWriteSerializer
from utils.envelope import Envelope


class ReviewViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def list(self, request):
        reviews = request.user.received_reviews.all()
        aggregate_data = reviews.aggregate(
            avg_rating=Avg("rating"), total_reviews=Count("id")
        )
        serializer = ReviewReadSerializer(reviews, many=True)
        return Envelope.success_response(
            data={
                "count": aggregate_data["total_reviews"],
                "average_rating": aggregate_data["avg_rating"],
                "reviews": serializer.data,
            }
        )

    def create(self, request):
        serializer = ReviewWriteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            data = serializer.save(reviewer=self.request.user)
            return Envelope.success_response(
                data=ReviewReadSerializer(data).data,
                status_code=status.HTTP_201_CREATED,
            )
        return Envelope.error_response(
            error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )


class UserReviewViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request, user_id):
        reviews = Review.objects.filter(reviewed_user=user_id)
        aggregate_data = reviews.aggregate(
            avg_rating=Avg("rating"), total_reviews=Count("id")
        )
        serializer = ReviewReadSerializer(
            reviews, many=True, context={"request": request}
        )
        return Envelope.success_response(
            data={
                "count": aggregate_data["total_reviews"],
                "average_rating": aggregate_data["avg_rating"],
                "reviews": serializer.data,
            }
        )
