# Candidate B: glibc workflow tools + exact upstream V2 musl executable.
ARG OPENCODE_SOURCE=ghcr.io/anomalyco/opencode:2.0.22@sha256:11f2b6c96d380867387fbee390c06cb47efffd9fdc37009b4cd40795b45dad19
ARG BASE_SOURCE=docker.io/library/debian:13-slim@sha256:a99cfc517144bc59b1978475ec53b46ecabec7e43635402ee5b77cc54cd1b20a
FROM ${OPENCODE_SOURCE} AS runtime
FROM ${BASE_SOURCE}
ARG DEBIAN_SNAPSHOT=20261007T140000Z
# Signed immutable indexes; HTTP bootstrap avoids an unpinned CA package install.
RUN rm /etc/apt/sources.list.d/debian.sources \
    && printf 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/%s/ trixie main\ndeb [check-valid-until=no] http://snapshot.debian.org/archive/debian/%s/ trixie-updates main\ndeb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/%s/ trixie-security main\n' "$DEBIAN_SNAPSHOT" "$DEBIAN_SNAPSHOT" "$DEBIAN_SNAPSHOT" > /etc/apt/sources.list \
    && apt-get -o Acquire::Retries=2 update \
    && apt-get install -y --no-install-recommends ca-certificates git ripgrep jq curl python3 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /bin/sh foreman \
    && mkdir -p /workspace /usr/share/agent-runtime \
    && chown foreman:foreman /workspace \
    && dpkg-query -W > /usr/share/agent-runtime/package-manifest.tsv
# Preserve the upstream executable and its musl dependencies as one source unit.
# Debian tools remain glibc-native. Do not silently substitute a V1 npm package.
COPY --from=runtime /usr/local/bin/opencode /usr/local/bin/opencode
COPY --from=runtime /lib/ld-musl-x86_64.so.1 /lib/ld-musl-x86_64.so.1
COPY --from=runtime /usr/lib/libstdc++.so.6 /usr/lib/opencode-musl/libstdc++.so.6
COPY --from=runtime /usr/lib/libgcc_s.so.1 /usr/lib/opencode-musl/libgcc_s.so.1
ENV HOME=/home/foreman XDG_CONFIG_HOME=/home/foreman/.config XDG_DATA_HOME=/home/foreman/.local/share XDG_STATE_HOME=/home/foreman/.local/state XDG_CACHE_HOME=/home/foreman/.cache
RUN printf '/usr/lib/opencode-musl\n/lib\n' > /etc/ld-musl-x86_64.path \
    && opencode --version | grep -Fx 'opencode v2.0.22' \
    && rm -rf /home/foreman/.local /home/foreman/.cache
COPY LICENSE.opencode /usr/share/agent-runtime/LICENSE.opencode
ARG SOURCE_REVISION=unreleased
USER 1000:1000
WORKDIR /workspace
LABEL org.opencontainers.image.version="2.0.22-runtime.1-candidate" \
      org.opencontainers.image.source="https://github.com/youling/ai-use" \
      org.opencontainers.image.revision="${SOURCE_REVISION}" \
      org.opencontainers.image.licenses="Apache-2.0 AND MIT" \
      org.opencontainers.image.description="OpenCode reference Foreman; runtime projected context and credentials"
ENTRYPOINT ["opencode"]
CMD ["serve", "--hostname", "0.0.0.0", "--port", "4096"]
