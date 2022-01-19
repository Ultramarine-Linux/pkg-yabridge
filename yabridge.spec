
#=============================================================================
# Overview of build options:
#
# End of build options
#-----------------------------------------------------------------------------
%undefine _disable_source_fetch
##trace

# force single job compilation
%define _smp_mflags -j1

%global debug_package    %{nil}

%global _lto_cflags      %{nil}

%global with_32bit       1
%global wineversion      7.0

#%%global bitseryversion   5.2.2
#%%global tomlversion      2.5.0
#%%global function2version 4.2.0
%global vst3sdkversion   v3.7.4_build_25-patched

%global gitdate          20220101
%global commit           e0ab24e64581dcd3c6367054ab670a8b7201b5d9
%global shortcommit      %(c=%{commit}; echo ${c:0:7})

%global version          3.8.0

# set this to "1" if building a git/beta/rc release
%global beta_or_rc       0


#=============================================================================
# general
#-----------------------------------------------------------------------------
Name:           yabridge
Version:        %{version}
%if %{beta_or_rc}
Release:        0.%{release}.%{gitdate}.git%{shortcommit}%{?dist}
%else
Release:        1%{?dist}
%endif
Summary:        Yet Another VST bridge, run Windows VST2 plugins under Linux
License:        GPLv3
URL:            https://github.com/robbert-vdh/yabridge
%if %{beta_or_rc}
Source0:        https://github.com/robbert-vdh/yabridge/archive/{commit}/%{name}-%{version}-git%{shortcommit}.tar.gz
#Source0:        https://github.com/robbert-vdh/yabridge/archive/yabridge-master.zip
%else
Source0:        https://github.com/robbert-vdh/yabridge/archive/%{version}/%{name}-%{version}.tar.gz
%endif
#Source1:        bitsery-%%{bitseryversion}.tar.gz
#Source2:        tomlplusplus-%%{tomlversion}.tar.gz
#Source3:        function2-%%{function2version}.tar.gz
# https://github.com/robbert-vdh/vst3sdk
# git clone && git submodule update --init
# ~/bin/git-archive-all.sh --format=tar.gz --prefix=vst3/ -o ../vst3sdk-v3.7.3_build_20-patched.tar.gz v3.7.3_build_20-patched
Source4:        https://github.com/robbert-vdh/vst3sdk/archive/refs/tags/%{vst3sdkversion}.tar.gz
BuildRequires:  cmake
BuildRequires:  cargo
BuildRequires:  meson >= 0.55
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  boost
BuildRequires:  boost-devel
BuildRequires:  boost-filesystem
BuildRequires:  boost-system
BuildRequires:  git-core
BuildRequires:  glibc-devel
BuildRequires:  libstdc++-devel
BuildRequires:  libxcb-devel
BuildRequires:  rust
BuildRequires:  rust-packaging
BuildRequires:  wine-devel = %{wineversion}
BuildRequires:  bitsery
BuildRequires:  tomlplusplus
BuildRequires:  function2
%if %{with_32bit}
BuildRequires:  boost(x86-32)
BuildRequires:  boost-devel(x86-32)
BuildRequires:  boost-filesystem(x86-32)
BuildRequires:  boost-iostreams(x86-32)
BuildRequires:  boost-system(x86-32)
BuildRequires:  glibc-devel(x86-32)
BuildRequires:  libstdc++-devel(x86-32)
BuildRequires:  libxcb-devel(x86-32)
BuildRequires:  wine(x86-32) = %{wineversion}
BuildRequires:  wine-core(x86-32) = %{wineversion}
BuildRequires:  wine-devel(x86-32) = %{wineversion}
%endif
BuildArch:      x86_64
Requires:       boost
Requires:       boost-filesystem
Requires:       boost-system
Requires:       libxcb
Requires:       libXau
%if %{with_32bit}
Requires:       glibc(x86-32)
Requires:       libgcc(x86-32)
Requires:       libstdc++(x86-32)
Requires:       libxcb(x86-32)
Requires:       libXau(x86-32)
%endif

%description
Yet Another way to use Windows VST plugins on Linux. Yabridge seamlessly
supports running both 64-bit Windows VST2 plugins as well as 32-bit Windows
VST2 plugins in a 64-bit Linux VST host. This project aims to be as
transparent as possible to achieve the best possible plugin compatibility
while also staying easy to debug and maintain.


#=============================================================================
# prep
#-----------------------------------------------------------------------------
%prep
%if %{beta_or_rc}
%autosetup -p1 -n %{name}
%else
%setup -qn %{name}-%{version}
%endif

# yabridgectl
cd tools/yabridgectl
%cargo_generate_buildrequires tools/yabridgectl
%generate_buildrequires
cd ../..

# copy required subprojects into subprojects/packagecache/
mkdir -p subprojects/packagecache

# bitsery
#cp -v %{SOURCE1} subprojects/packagecache/bitsery-v%{bitseryversion}.tar.gz

# tomlplusplus
#cp -v %{SOURCE2} subprojects/packagecache/tomlplusplus-v%{tomlversion}.tar.gz

# function2
#cp -v %{SOURCE3} subprojects/packagecache

# unpack stuff and patch
pushd subprojects/

# toml
#unzip %{SOURCE2}
#mv -v tomlplusplus-%{tomlversion} tomlplusplus

# function2
#tar -xzf %{SOURCE3}
#tar -xJf function2-patch-4.1.0.tar.xz

# vst3sdk
tar -xzf %{SOURCE4}
popd

# set possible newer version in meson.build (dev builds) only on line 4
%if %{beta_or_rc}
sed -i -e"4s|^  version : '.*$|  version : '%{version}',|" meson.build
%endif

#echo "" >> cross-wine.conf
#echo "cpp_args = ['-v']" >> cross-wine.conf


#=============================================================================
# build
#-----------------------------------------------------------------------------
%build

%if %{with_32bit}
#meson setup --buildtype=release --cross-file cross-wine.conf \
#  -Dwith-bitbridge=true --unity=on --unity-size=1000 \
#  build
%meson -Dwith-bitbridge=true --unity=on --unity-size=1000 --cross-file cross-wine.conf --buildtype=release
%else
#meson setup --buildtype=release --cross-file cross-wine.conf \
#  -Dwith-bitbridge=false --unity=on --unity-size=1000 \
#  build
%meson --buildtype=release --cross-file cross-wine.conf -Dwith-bitbridge=false --unity=on --unity-size=1000
%endif

%meson_build

pushd tools/yabridgectl
%cargo_build
popd


#=============================================================================
# check
#-----------------------------------------------------------------------------
%check
# there are no tests
# ninja test -v -j1 -C build test


#=============================================================================
# install
#-----------------------------------------------------------------------------
%install
# create directories
install -d -m0755 %{buildroot}%{_bindir}
install -d -m0755 %{buildroot}%{_libdir}

# install apps and libs
install -D -m 0755 build/yabridge-group*.exe* %{buildroot}%{_bindir}/
install -D -m 0755 build/yabridge-host*.exe* %{buildroot}%{_bindir}/
install -D -m 0755 build/libyabridge-vst*.so %{buildroot}%{_libdir}/

# install tool
pushd tools/yabridgectl
%cargo_install
#install -D -m 0755 tools/yabridgectl/target/release/yabridgectl %{buildroot}%{_bindir}/


#=============================================================================
# files
#-----------------------------------------------------------------------------
%files
%defattr(-,root,root)
%license COPYING
%doc CHANGELOG.md README.md
%attr(0755,root,root)        %{_bindir}/yabridgectl
%attr(0755,root,root)        %{_bindir}/yabridge-group.exe
%attr(0755,root,root)        %{_bindir}/yabridge-group.exe.so
%attr(0755,root,root)        %{_bindir}/yabridge-host.exe
%attr(0755,root,root)        %{_bindir}/yabridge-host.exe.so
%if %{with_32bit}
%attr(0755,root,root)        %{_bindir}/yabridge-group-32.exe
%attr(0755,root,root)        %{_bindir}/yabridge-group-32.exe.so
%attr(0755,root,root)        %{_bindir}/yabridge-host-32.exe
%attr(0755,root,root)        %{_bindir}/yabridge-host-32.exe.so
%endif
%attr(0755,root,root)        %{_libdir}/libyabridge-vst2.so
%attr(0755,root,root)        %{_libdir}/libyabridge-vst3.so


#=============================================================================
# post
#-----------------------------------------------------------------------------
%post
/sbin/ldconfig


#=============================================================================
# postun
#-----------------------------------------------------------------------------
%postun
/sbin/ldconfig


#=============================================================================
# changelog
#-----------------------------------------------------------------------------
%changelog
* Sat Jan 01 2022 Patrick Laimbock <patrick@laimbock.com> - 3.7.1-0.3
- update to git rev e0ab24e64581dcd3c6367054ab670a8b7201b5d9
- require meson >= 0.55
- build against wine-7.0rc3

* Sun Dec 05 2021 Patrick Laimbock <patrick@laimbock.com> - 3.7.1-0.2
- build against wine-6.23

* Sun Dec 05 2021 Patrick Laimbock <patrick@laimbock.com> - 3.7.1-0.1
- update to git rev e4b2a383309dc6020945d2c2dbb5425a70f6e05b

* Sun Nov 21 2021 Patrick Laimbock <patrick@laimbock.com> - 3.7.0-1
- update to version 3.7.0

* Thu Nov 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.6.1-0.5
- update to git rev a94be5638781d962ee20c95afd216843e9e443d0
- let yabridge download bitsery, function2 and tomlplusplus since it
- already does the same for all the yabridgectl deps

* Sun Nov 07 2021 Patrick Laimbock <patrick@laimbock.com> - 3.6.1-0.4
- update to git rev dd6144333a6d065cda8fd38bab1f79e0dbaaed34
- build against wine-6.21

* Sat Oct 23 2021 Patrick Laimbock <patrick@laimbock.com> - 3.6.1-0.3
- update to git rev 5be149cb525a638f7fc3adf84918c8239ee50ecf
- counters https://bugs.winehq.org/show_bug.cgi?id=51919

* Sat Oct 23 2021 Patrick Laimbock <patrick@laimbock.com> - 3.6.1-0.2
- build against wine-6.20

* Thu Oct 21 2021 Patrick Laimbock <patrick@laimbock.com> - 3.6.1-0.1
- update to git rev 0382b0a475480779a968b81f713af3c58ac80884

* Sat Oct 09 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.6
- update to git rev cfc0591ca9dfa0b11cce6bb3fe699c455bcbc1a1
- build against wine-6.19

* Thu Oct 07 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.5
- update to git rev c18332f7d4178416152af5538881a091cdf819ca
- build against wine-6.18

* Sat Sep 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.4
- update to git rev f8703bb49c1820d9b1e8148d863a2d11166dcc09
- build against wine-6.17

* Sat Aug 28 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.3
- build against wine-6.16

* Tue Aug 24 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.2
- update to git rev a1cbf23f66166608174d57ec783f750caf0b2ff7

* Wed Aug 18 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.3-0.1
- update to git rev 5bf3b971189d64f098e89d64468a2c1ec81a56a6

* Sat Aug 14 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.2-2
- build against wine-6.15

* Sun Aug 08 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.2-1
- update to version 3.5.2

* Fri Aug 06 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.2-0.2
- update to git rev 9160de648365ddedfa8ae759ba6691ed7753ed0f

* Mon Aug 02 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.2-0.1
- update to git rev 2e6732c0e2932ee623c2a8cb9e2f1a17225ff941

* Sun Aug 01 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.1-1
- update to version 3.5.1

* Sat Jul 31 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.1-0.1
- update to git rev e430c5f0155417f1bb9572be0816d95155e3f2fd

* Sat Jul 24 2021 Patrick Laimbock <patrick@laimbock.com> - 3.5.0-1
- update to version 3.5.0

* Thu Jul 22 2021 Patrick Laimbock <patrick@laimbock.com> - 3.4.1-0.4
- update to git rev 8108e08dbfddf678f9505c2f854ae39d27e8319c

* Thu Jul 22 2021 Patrick Laimbock <patrick@laimbock.com> - 3.4.1-0.3
- build against wine-6.13
- update to git rev 1e47390edc2258a2aa1e7deccc3144dc5bf1370b

* Tue Jul 20 2021 Patrick Laimbock <patrick@laimbock.com> - 3.4.1-0.2
- update to git rev 640c188338acdbd5e21664fac4ab6827fdc9f8ac

* Mon Jul 19 2021 Patrick Laimbock <patrick@laimbock.com> - 3.4.1-0.1
- update to git rev 503720a9ca5782035ffbf41330e66fc9f4fbf045

* Thu Jul 15 2021 Patrick Laimbock <patrick@laimbock.com> - 3.4.0-1
- update to version 3.4.0

* Tue Jul 13 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.14
- update to git rev a2b877b101512e7dd621c30d123a0118467a889a

* Mon Jul 12 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.13
- update to git rev 11d3ec90108c2929abe69a44c50c3db39535abd3

* Sun Jul 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.12
- update to git rev 1b4c4ecfaddb585ec64dbc57b787a7658516ed01

* Sun Jul 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.11
- update to git rev b1b47ec80dc520e7feec83775910a84c5ec603c5

* Sun Jul 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.10
- update to git rev d21073f8660d77a798506857d9498d7490c86499

* Sun Jul 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.9
- update to git rev 4e67fa92128d54ab12544b489628482f404ba960

* Sun Jul 11 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.8
- update to git rev 6f3beca32af75a47255a5c9b37d17bbad50b24c4

* Sat Jul 10 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.7
- update to git rev 94125f9eab52093558294ef685095b7a36be2edc

* Sat Jul 10 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.6
- update to git rev 92daa33adfba7273f5ebd25544ebe242c5bf4c57

* Sat Jul 10 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.5
- update to git rev 1946693244f5f862c60805d733468dfc056b0b4a
- build against wine-6.12

* Wed Jul 07 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.4
- update to git rev a58a1ab111abd73b0cb014b9ac4c9edcf3a3f01b

* Sat Jul 03 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.3
- update to git rev c13d8f2ee3fcdb5beb6b8c9c5e8b1d421464ca86

* Sun Jun 27 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.2
- update to git rev e0713c5fe7da9d52268bcabf0ae90e14fd2e2345

* Sun Jun 13 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.2-0.1
- update to git rev 42e1e49ab983e909c0dcb9259aa140b5d7e57c06

* Thu Jun 10 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.1-1
- update to version 3.3.1

* Sun Jun 06 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.0-2
- build against wine-6.10

* Fri Jun 04 2021 Patrick Laimbock <patrick@laimbock.com> - 3.3.0-1
- update to version 3.3.0

* Tue Jun 01 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.9
- update to git rev 712ef41a7fc814fc873d398b7299ce971619cbda

* Mon May 31 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.8
- update to git rev 5f4ffed90bb4f0eed9731d020daa35fb2e34d0f2

* Sun May 30 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.7
- update to git rev db0f58d0009ead6ba7547f514032f25c5fda9e7e

* Tue May 25 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.6
- update to git rev 4d5b2fcb12c7f08f0f971c0873e554d8cb303740

* Sun May 23 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.5
- update to git rev 0b9b1330ad9aabc238f7d3c335d1485a74b36606
- build against wine-6.9
- more optimizations!

* Sat May 22 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.4
- update to git rev 7c49fe739df2a9b83984c8c4e0db926dd5b6067d
- performance enhancements!

* Wed May 19 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.3
- update to git rev 4d256e12e2b6d6180bf117d68e960cfd859e6719
- adds disable_pipes option to make UJAM/Loopmaster/Gorilla SDK plugins work

* Mon May 17 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.2
- update to git rev 09c2ed96adb0480a20eeaa8b03260c56e4c10956

* Sun May 09 2021 Patrick Laimbock <patrick@laimbock.com> - 3.2.1-0.1
- update to git rev db6ecdbbd4ae4452637a89e21e893570d78d0018

* Fri Apr 30 2021 Patrick Laimbock <patrick@laimbock.com> - 3.1.1-0.2
- update to git rev 89d6c1b2e0cc9253c745dc73f7c152cbc426eb4f
- fixes a segfault occuring in several but not all libstdc++ versions

* Sun Apr 25 2021 Patrick Laimbock <patrick@laimbock.com> - 3.1.1-0.1
- update to git rev 671c6a4c1812afb8261a83c3328ce064a7e88bc6
- build against wine-6.7

* Mon Apr 19 2021 Patrick Laimbock <patrick@laimbock.com> - 3.1.0-2
- rebuild against wine-6.6 with backported fix for BZ50996

* Thu Apr 15 2021 Patrick Laimbock <patrick@laimbock.com> - 3.1.0-1
- update to version 3.1.0

* Thu Apr 15 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.3-0.2
- update to git rev 4eb0490fdeb70270d70c4d0d60491d8b7d0e736c

* Mon Apr 12 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.3-0.1
- update to git rev 266d22b051ce7870dbc73045c91a0368fc3d78b8
- build against wine-6.5

* Mon Mar 15 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.2-2
- add patch for missing include

* Mon Mar 08 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.2-1
- update to version 3.0.2

* Sat Feb 27 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.1-1
- update to version 3.0.1
- build against wine-6.3

* Tue Feb 23 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.1-0.1
- update to git rev a6ac958bfb467e3e0e789cf0c64475bb32b383c6
- includes fix for a REAPER segfault
- includes fix for wine 6.3 regression

* Sun Feb 21 2021 Patrick Laimbock <patrick@laimbock.com> - 3.0.0-1
- update to version 3.0.0

* Sat Feb 13 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.12
- update to git rev 4e4ed3a6b46845a67eba90333309051bf1a9e672
- drop patch which is now in upstream

* Thu Feb 04 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.11
- add yabridgectl_use_usr_lib64.patch which makes yabridgectl look in /usr/lib64

* Tue Feb 02 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.10
- update to git rev 391206eea86eaffd91441ec2e1809d558f64fe14

* Sat Jan 30 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.9
- update to git rev 81d401f06a0d3908dbac0785dd2475545f43f8fa

* Sat Jan 30 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.8
- update to git rev 68bf2029b3100dd6e88876e607f7d444b729ba7a

* Wed Jan 27 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.7
- update to git rev 04d0ff094911edc9423001c8fd26d326e858f673

* Sat Jan 23 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.6
- update to git rev d5e44244631e7e31110d4e5c6f0ba09dc7d71b88

* Thu Jan 21 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.5
- update to git rev 2ca1d5b8caa53d65a052a97047e43f7551e42474
- add the yabridgectl utility

* Mon Jan 11 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.4
- test build from the feature/non-realtime-event-loop branch
- git rev 3ca70616590cc5161863d5647035d358534d1a53

* Sun Jan 10 2021 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.3
- update to git rev c938068cf53a235bb6c85fbd922049ac14bd78d9
- use vst3sdk git rev e2fbb41f28a4b311f2fc7d28e9b4330eec1802b6
- build against wine-staging-6.0-rc6

* Sun Jan 03 2021 Patrick Laimbock <patrick@laimbock.com - 2.2.2-0.2
- update to git rev 71eadff1edd6f9e54ab608e828cdd6f4b9e9f28c
- build against wine-6.0-rc5

* Mon Dec 21 2020 Patrick Laimbock <patrick@laimbock.com> - 2.2.2-0.1
- update to git rev 6ef740e0b0a67fddfa19dcbf1c8d11a2f12ed103
- build against wine-6.0rc3

* Fri Dec 18 2020 Patrick Laimbock <patrick@laimbock.com> - 2.2.1-1
- update to version 2.1.2
- build against wine 6.0rc2

* Sun Nov 29 2020 Patrick Laimbock <patrick@laimbock.com> - 2.1.1-0.1
- update to git rev cbf276b7dc9d8a9b0d50c46fd48ebfc293dd809b

* Thu Nov 26 2020 Patrick Laimbock <patrick@laimbock.com> - 2.1.0-2
- build against wine 5.22

* Fri Nov 20 2020 Patrick Laimbock <patrick@laimbock.com> - 2.1.0-1
- update to version 2.1.0

* Sat Nov 14 2020 Patrick Laimbock <patrick@laimbock.com> - 2.0.3-0.1
- update to git rev 005ae61e0825500f5a71419b30d78e11382f8502
- from branch bitwig-3.3-beta-hack to work around plugin load issue

* Mon Nov 09 2020 Patrick Laimbock <patrick@laimbock.com> - 2.0.1-1
- update to version 2.0.1

* Sun Nov 08 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.2-0.3
- update to git rev 889d9d81c4c2033e229c831fa5e0d79b9b480293

* Sat Nov 07 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.2-0.2
- update to git rev 42032c5c2dfda0aa3844a67adc091a0994418822

* Sat Nov 07 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.2-0.1
- update to git rev 23cd2dd1933b628c4c33298deeac428bd90d1056

* Tue Oct 27 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.1-2
- build against wine 5.20

* Fri Oct 23 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.1-1
- update to version 1.7.1

* Fri Oct 23 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.1-0.2
- update to git rev c2ec1ce9943f2bf2efd8c705e786c5cb659a2499

* Sat Oct 17 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.1-0.1
- update to HEAD

* Sat Oct 17 2020 Patrick Laimbock <patrick@laimbock.com> - 1.7.0-1
- update to version 1.7.0

* Wed Sep 30 2020 Patrick Laimbock <patrick@laimbock.com> - 1.6.1-1
- update to version 1.6.1

* Wed Sep 09 2020 Patrick Laimbock <patrick@laimbock.com> - 1.6.0-1
- update to version 1.6.0
- build against wine 5.17

* Wed Sep 09 2020 Patrick Laimbock <patrick@laimbock.com> - 1.5.0-2
- build against wine 5.16

* Sun Aug 23 2020 Patrick Laimbock <patrick@laimbock.com> - 1.5.0-1
- update to version 1.5.0

* Sun Aug 16 2020 Patrick Laimbock <patrick@laimbock.com> - 1.4.2-0.1
- update to git rev ebe1a9c64962a2e41dc8df2e9f0f3bdad5aaf65e

* Sun Aug 16 2020 Patrick Laimbock <patrick@laimbock.com> - 1.4.1-1
- update to version 1.4.1

* Sun Jul 19 2020 Patrick Laimbock <patrick@laimbock.com> - 1.3.0-1
- update to version 1.3.0

* Sat Jun 06 2020 Patrick Laimbock <patrick@laimbock.com> - 1.2.1-0.1
- update to git rev 4403585a7075b1b06fd75a8ea31eb3bbf9101545

* Tue Jun 02 2020 Patrick Laimbock <patrick@laimbock.com> - 1.2.0-1
- update to version 1.2.0
- build against wine 5.9-2

* Sun May 17 2020 Patrick Laimbock <patrick@laimbock.com> - 1.1.5-0.1
- initial release for Fedora 32
- use git rev e728dbe5a2262d9df931c93c651b053d7a80b5e5

