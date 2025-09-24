from django.db.models import Avg, Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.viewsets import ViewSet

from apps.permissions import IsEmailVerified, IsReviewOwner
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewReadSerializer, ReviewWriteSerializer
from utils.envelope import Envelope


class ReviewViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified, IsReviewOwner]

    def get_object(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        self.check_object_permissions(self.request, review)
        return review

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

    def destroy(self, request, review_id):
        try:
            obj = self.get_object()
        except Http404:
            return Envelope.error_response(
                error="review not found", status_code=status.HTTP_404_NOT_FOUND
            )
        obj.delete()
        return Envelope.success_response(data={"message": "review deleted"})


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
