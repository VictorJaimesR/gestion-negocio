import logging
import time

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response


logger = logging.getLogger(__name__)


class InstrumentedAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class InstrumentedObtainAuthToken(ObtainAuthToken):
    serializer_class = InstrumentedAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        request_started = time.perf_counter()
        request_cpu_started = time.process_time()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user_model = get_user_model()

        lookup_started = time.perf_counter()
        lookup_cpu_started = time.process_time()
        try:
            user = user_model._default_manager.get_by_natural_key(username)
        except user_model.DoesNotExist:
            user = None
        lookup_ms = (time.perf_counter() - lookup_started) * 1000
        lookup_cpu_ms = (time.process_time() - lookup_cpu_started) * 1000

        hash_ms = None
        hash_cpu_ms = None
        authenticated = False
        if user is not None:
            hash_started = time.perf_counter()
            hash_cpu_started = time.process_time()
            authenticated = user.check_password(password)
            hash_ms = (time.perf_counter() - hash_started) * 1000
            hash_cpu_ms = (time.process_time() - hash_cpu_started) * 1000

        if not authenticated or not user.is_active:
            logger.info(
                'login_timing result=failed lookup_ms=%.2f lookup_cpu_ms=%.2f '
                'hash_ms=%s hash_cpu_ms=%s total_ms=%.2f total_cpu_ms=%.2f',
                lookup_ms,
                lookup_cpu_ms,
                f'{hash_ms:.2f}' if hash_ms is not None else 'not_run',
                f'{hash_cpu_ms:.2f}' if hash_cpu_ms is not None else 'not_run',
                (time.perf_counter() - request_started) * 1000,
                (time.process_time() - request_cpu_started) * 1000,
            )
            raise serializers.ValidationError(
                'Unable to log in with provided credentials.',
                code='authorization',
            )

        token_started = time.perf_counter()
        token_cpu_started = time.process_time()
        token, created = Token.objects.get_or_create(user=user)
        token_ms = (time.perf_counter() - token_started) * 1000
        token_cpu_ms = (time.process_time() - token_cpu_started) * 1000
        logger.info(
            'login_timing result=success algorithm=%s iterations=%s '
            'lookup_ms=%.2f lookup_cpu_ms=%.2f hash_ms=%.2f hash_cpu_ms=%.2f '
            'token_ms=%.2f token_cpu_ms=%.2f total_ms=%.2f total_cpu_ms=%.2f '
            'token_created=%s',
            identify_hasher(user.password).algorithm,
            identify_hasher(user.password).iterations
            if hasattr(identify_hasher(user.password), 'iterations')
            else 'n/a',
            lookup_ms,
            lookup_cpu_ms,
            hash_ms,
            hash_cpu_ms,
            token_ms,
            token_cpu_ms,
            (time.perf_counter() - request_started) * 1000,
            (time.process_time() - request_cpu_started) * 1000,
            created,
        )
        return Response({'token': token.key})
