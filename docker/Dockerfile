FROM python:3.12

# RUN apt-get update -qq && apt-get install -y \
#     wget \
#     libswitch-perl \
#     gnupg \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*
#
# COPY ./texlive.profile /tmp/
# RUN cd /tmp && wget -qO- https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar xz \
#     && /tmp/install-tl*/install-tl -profile /tmp/texlive.profile \
#     && rm -rf /tmp/install-tl-*
#
# ENV PATH="/usr/local/texlive/bin/x86_64-linux:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY --from=texlive/texlive:latest /usr/local/texlive /usr/local/texlive

RUN $(find /usr/local/texlive -name tlmgr) path add && \
    # Temporary fix for ConTeXt (#30)
    (sed -i '/package.loaded\["data-ini"\]/a if os.selfpath then environment.ownbin=lfs.symlinktarget(os.selfpath..io.fileseparator..os.selfname);environment.ownpath=environment.ownbin:match("^.*"..io.fileseparator) else environment.ownpath=kpse.new("luatex"):var_value("SELFAUTOLOC");environment.ownbin=environment.ownpath..io.fileseparator..(arg[-2] or arg[-1] or arg[0] or "luatex"):match("[^"..io.fileseparator.."]*$") end' /usr/bin/mtxrun.lua || true)