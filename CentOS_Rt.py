# CentOS 7.2 Integrate rtorrent installation
import os
import time
import random
import string
import urllib2
import platform
import argparse
import subprocess

httpfolder = "/usr/share/nginx/html/"
rtorrentuser = ""
password = ""

# Rtorrent Enviroment
new_env = os.environ.copy()
new_env['PKG_CONFIG_PATH'] = "/usr/local/lib/pkgconfig"


class SysRelated(object):
    distribution = platform.linux_distribution()

    def __init__(self):
        self.checkSystem()
        self.checkSysVersion()
        #self.checkRoot()
        return

    # System check
    @staticmethod
    def checkSystem():
        os = SysRelated.distribution[0]
        if "CentOS" in os:
            return
        print "Your system doesn't compatible with the script"
        exit(1)
        return

    # System version check
    @staticmethod
    def checkSysVersion():
        versions = SysRelated.distribution[1]
        version = versions.split(".")
        if version[0] == "7":
            return
        print "Your system version doesn't compatible with the script"
        exit(1)
        return

    # #Root check
    # @staticmethod
    # def checkRoot():
    #     uid = os.geteuid()
    #     if uid != 0:
    #         print "You need root permissions to run this script"
    #         exit(1)
    #     return

# Install dependency of rtorrent
class Rtorrent(object):
    # Initial function
    def __init__(self, lversion = "0.13.6", rversion = "0.9.6"):
        self.lversion = lversion
        self.rversion = rversion
        self.installSystemDependency()
        self.getSourceCode(lversion, rversion)
        self.compileSource()
        self.getConfig()
        self.startRtorrent()
        self.installRutorrent()
        return

    # system dependency installation
    def installSystemDependency(self):
        p1 = subprocess.check_call(
            ["yum", "groupinstall", "-y", "Development Tools"], shell=False)
        p2 = subprocess.check_call(["yum", "install", "-y", "cppunit-devel", "libtool", "zlib-devel",
                                    "gawk", "libsigc++20-devel", "openssl-devel", "ncurses-devel", "libcurl-devel",
                                    "xmlrpc-c-devel", "unzip", "screen"], shell=False)
        return

    # Initial function
    def getSourceCode(self, lversion, rversion):
        self.getLibtorrent(lversion)
        self.getRtorrent(rversion)
        return

    # Get libtorrent from Github
    def getLibtorrent(self, lversion):
        try:
            os.chdir("/root")
            p1 = subprocess.check_call(
                "wget https://github.com/rakshasa/libtorrent/archive/v" + lversion + ".tar.gz", shell=True)
            subprocess.check_call(
                "tar xf v " + lversion + ".tar.gz", shell = True)
        except:
            print "Get libtorrent error"
            exit(1)
        return

    # Get rtorrent from Github
    def getRtorrent(self, rversion):
        try:
            os.chdir("/root")
            p1 = subprocess.check_call(
                "wget https://github.com/rakshasa/rtorrent/archive/v" + rversion + ".tar.gz", shell=True)
            subprocess.check_call(
                "tar xf v " + rversion + ".tar.gz", shell = True)
        except:
            print "Get rtorrent error"
            exit(1)
        return

    def compileSource(self):
        self.goToLibtorrentDirectory()
        self.configureLibtorrent()
        self.compileLibtorrent()
        self.goToRtorrentDirectory()
        self.configureRtorrent()
        self.compileLibtorrent()

        return

    # Go to libtorrent directory
    def goToLibtorrentDirectory(self):
        # Go to the libtorrent source code directory
        os.chdir("/root/libtorrent-" + self.lversion)
        return

    # Configure Makefile
    def configureLibtorrent(self):
        #autogen and check
        output1 = subprocess.check_output(
            ["/root/libtorrent/autogen.sh"]).decode('utf-8')
        if "ready to configure" not in output1:
            print "autogen error"
            exit(1)

        #configure and check
        output2 = subprocess.check_output(
            ["/root/libtorrent/configure", "--disable-debug"]).decode('utf-8')
        if "executing depfiles commands" not in output2:
            print "configure error"
            exit(1)
        return

    # Compile libtorrent
    def compileLibtorrent(self):
        #Compile and check
        output3 = subprocess.check_output(
            "make -j$(nproc)", shell=True).decode('utf-8')
        if "Error" in output3:
            print "Compilation error"
            exit(1)

        # Installation
        p3 = subprocess.check_call(["make", "install"])
        # Go back home
        p4 = os.chdir("/root")
        return

    def goToRtorrentDirectory(self):
        # Go to the rtorrent directory
        os.chdir("/root/rtorrent-" + self.rversion)
        return

    # Configure Makefile
    def configureRtorrent(self):
        #autogen and check
        output1 = subprocess.check_output(
            ["/root/rtorrent/autogen.sh"]).decode('utf-8')
        if "ready to configure" not in output1:
            exit(1)

        #configure and check
        output2 = subprocess.check_output(["/root/rtorrent/configure", "--with-xmlrpc-c",
                                           "--with-ncurses", "--enable-ipv6", "--disable-debug"], env=new_env).decode('utf-8')
        if "executing depfiles commands" not in output2:
            exit(2)
        return

    def getConfig(self):
        RtorrentConfig()
        return

    def startRtorrent(self):
        p0 = subprocess.check_call(
            "sudo -u " + rtorrentuser + " screen -dmS rtorrent /usr/local/bin/rtorrent", shell=True)
        return

    def installRutorrent(self):
        Rutorrent()
        return

# Rtorrent Installation and running verification
class RtorrentRunningVerification(object):
    # Initial function
    def __init__(self):
        self.runRtorrent()
        self.checkRtorrent()
        self.killRtorrent()
        return

    # Run rtorrent
    def runRtorrent(self):
        self.p1 = subprocess.Popen(["screen", "-dmS", "rtorrent", "rtorrent"])
        return

    # Check rtorrent
    def checkRtorrent(self):
        p2 = subprocess.check_output(["ps", "-ef"])
        if "rtorrent" not in p2:
            exit(1)
        return

    # Kill rtorrent
    def killRtorrent(self):
        p3 = subprocess.check_call(["pkill", "rtorrent"])
        return

# Get config file for rtorrent
class RtorrentConfig(object):
    # Initial funcition
    def __init__(self):
        self.creatUserForRtorrent()
        self.mkdirSessionAndDownload()
        self.getConfigFileFromWeb()
        self.openPort()
        return

    # Creat rtorrent user
    def creatUserForRtorrent(self):
        global username
        username = "rtuser"
        p0 = subprocess.check_call(["adduser", username])
        return

    # Creat session and download directory
    def mkdirSessionAndDownload(self):
        p0 = subprocess.check_call("mkdir /.session", shell=True)
        p1 = subprocess.check_call(
            "mkdir /home/" + username + "/rtdownloads", shell=True)
        p2 = subprocess.check_call("chmod -R 777 /.session", shell=True)
        return

    # Get config file from github
    def getConfigFileFromWeb(self):
        # Go to home directory
        p0 = subprocess.call("cd ~", shell=True)
        # Get File
        try:
            p1 = subprocess.check_call(
                "wget https://github.com/GalaxyXL/SeedBox_CentOS/raw/master/conf/rtorrent.rc", shell=True)
        except:
            print "error"

        # Change file content and name
        p2 = subprocess.check_call(
            "sed -i \"s/<username>/" + username + "/g\" rtorrent.rc", shell=True)
        p3 = subprocess.check_call(
            ["mv", "rtorrent.rc", "/home/" + username + "/.rtorrent.rc"])
        return

    # Firewall port setting
    def openPort(self):
        p0 = subprocess.check_call(
            "iptables -I INPUT -p tcp --dport 53698 -j ACCEPT", shell=True)
        p0 = subprocess.check_call(
            "iptables -I INPUT -p tcp --dport 80 -j ACCEPT", shell=True)
        return

# Install Nginx and related dependency and set config file
class Rutorrent(object):
    # Initial function
    def __init__(self):
        self.installNginx()
        self.installRelatedDependency()
        self.setNginxConfigFile()
        self.setPhpFpmConfig()
        self.setPhpGeoIpConfig()
        self.setPassWordForRutorrent(password)
        self.getRutorrent()
        self.getRutorrentPlugin()
        self.startNginxAndPhpFpm()
        return

    # Install Nginx from epel-release
    def installNginx(self):
        p0 = subprocess.check_call(["yum", "install", "-y", "epel-release"])
        p1 = subprocess.check_call(["yum", "install", "-y", "nginx"])
        return

    # Install related dependency
    def installRelatedDependency(self):
        p2 = subprocess.check_call(
            "yum install -y php-fpm httpd-tools php-cgi php-cli curl", shell=True)
        return

    # Nginx config file set
    def setNginxConfigFile(self):
        try:
            os.chdir("/etc/nginx")
            os.system(
                "wget https://github.com/GalaxyXL/SeedBox_CentOS/raw/master/conf/nginx.conf -O nginx.conf")
        except:
            print "Error Nginx config file"
            exit(1)
        return

    # Php-fpm config file set
    def setPhpFpmConfig(self):
        p0 = subprocess.check_call(
            "sed -i \"s/apache/" + rtorrentuser + "/g\" /etc/php-fpm.d/www.conf", shell=True)
        return

    # PHP-GeoIP config
    def setPhpGeoIpConfig(self):
        p0 = subprocess.check_call("yum install php-pecl-geoip -y", shell=True)
        p1 = subprocess.check_call(
            "rm -f /usr/share/GeoIP/GeoIP.dat", shell=True)
        p2 = subprocess.check_call("cd /usr/share/GeoIP", shell=True)
        p3 = subprocess.check_call(
            "wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz", shell=True)
        p4 = subprocess.check_call("gunzip GeoIP.dat.gz", shell=True)
        p5 = subprocess.check_call("cd ~", shell=True)
        return

    # Set rutorrent password
    def setPassWordForRutorrent(self, password):
        # Creat password file
        p0 = subprocess.check_call(
            ["htpasswd", "-cb", "/etc/nginx/rtpass", username, password])
        return

    # Start Nginx and PHP-FPM
    def startNginxAndPhpFpm(self):
        try:
            p0 = subprocess.check_output(
                "systemctl start nginx.service", shell=True)
            p1 = subprocess.check_call(
                "systemctl enable nginx.service", shell=True)
        except:
            print "Start Nginx Error"
            exit(1)
        try:
            p2 = subprocess.check_output("php-fpm -D", shell=True)
        except:
            print "Start Php-Fpm Error"
            exit(1)
        return

    # Download Rutorrent
    def getRutorrent(self):
        try:
            p0 = subprocess.check_call(
                "git clone https://github.com/Novik/ruTorrent.git " + httpfolder + "rutorrent", shell=True)
        except:
            print "Download Rutorrent Error"
        p1 = subprocess.check_call(
            "chown " + rtorrentuser + " -R /usr/share/nginx/html/rutorrent/share", shell=True)
        return

    # Rutorrent plugin
    def getRutorrentPlugin(self):
        try:
            p0 = subprocess.check_call(
                "rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7", shell=True)
            p0 = subprocess.check_call(
                "rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro", shell=True)
            p0 = subprocess.check_call(
                "rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm", shell=True)
            p1 = subprocess.check_call(
                "yum install -y ffmpeg unzip mediainfo rar unrar sox", shell=True)
        except:
            print "Rutorrent plugin install error"
        return

# Qbittorrent installation related
class Qbittorrent(object):
    def __init__(self, version = "4.0.4"):
        self.version = version
        os.chdir("/root")
        self.installDependency()
        self.getLibtorrentRasterbar()
        self.configureLibtorrentRasterbar()
        self.getQbittorrent()
        self.configureQbittorrent()
        self.openPort()
        return

    # Install qt5 and development tools
    def installDependency(self):
        subprocess.check_output(
            "yum -y groupinstall \"Development Tools\"", shell=True)
        subprocess.check_output(
            "yum -y install qt-devel boost-devel openssl-devel qt5-qtbase-devel qt5-linguist", shell=True)
        return

    # Get libtorrent-rasterbar from web
    def getLibtorrentRasterbar(self):
        try:
            subprocess.check_call(
                "wget https://github.com/arvidn/libtorrent/releases/download/libtorrent-1_1_5/libtorrent-rasterbar-1.1.5.tar.gz", shell=True)
            subprocess.check_call(
                "tar xf libtorrent-rasterbar-1.1.5.tar.gz", shell=True)
        except:
            print "Get libtorrent-rasterbar error"
        return

    # configure and compile libtorrent-rasterbar
    def configureLibtorrentRasterbar(self):
        os.chdir("/root/libtorrent-rasterbar-1.1.5")
        os.system("./configure --disable-debug --prefix=/usr CXXFLAGS=-std=c++11")
        os.system("make")
        os.system("make install")

        # establish soft link
        subprocess.check_call(
            "ln -s /usr/lib/pkgconfig/libtorrent-rasterbar.pc /usr/lib64/pkgconfig/libtorrent-rasterbar.pc", shell=True)
        subprocess.check_call(
            "ln -s /usr/lib/libtorrent-rasterbar.so.9 /usr/lib64/libtorrent-rasterbar.so.9", shell=True)
        os.chdir("/root")
        return

    # Get qbittorrent from web
    def getQbittorrent(self):
        try:
            subprocess.check_call(
                "wget https://github.com/qbittorrent/qBittorrent/archive/release-" + self.version + ".tar.gz", shell=True)
            subprocess.check_call("tar xf release-" + self.version + ".tar.gz", shell=True)
        except:
            print "Get Qbittorrent error"
        return

    # Configure and compile qbittorrent
    def configureQbittorrent(self):
        os.chdir("qBittorrent-release-" + self.version)
        os.system(
            "./configure --disable-debug --prefix=/usr --disable-gui CPPFLAGS=-I/usr/include/qt5  CXXFLAGS=-std=c++11")
        os.system("make")
        os.system("make install")
        os.chdir("/root")
        print "qbittorrent install complete"
        return

    # Open port
    def openPort(self):
        subprocess.check_call(
            "iptables -I INPUT -p tcp --dport 8080 -j ACCEPT", shell=True)
        subprocess.check_call(
            "iptables -I INPUT -p tcp --dport 8999 -j ACCEPT", shell=True)
        return

# Deluge installation related
class Deluge(object):
    def __init__(self, version = "1.3.15"):
        self.version = version
        self.installDependency()
        self.downloadSource()
        self.installDeluge()
        self.startDeluge()
        self.openPort()
        return

    def installDependency(self):
        subprocess.check_call(
            "yum install epel-release -y", shell = True)
        subprocess.check_call(
            "yum install python python-twisted-core python-twisted-web pyOpenSSL \
            python-setuptools gettext intltool pyxdg python-chardet python-GeoIP \
            rb_libtorrent-python2 python-setproctitle python-pillow python-mako -y", shell = True)
        return

    def downloadSource(self):
        os.chdir("/root")
        subprocess.check_call(
            "wget http://download.deluge-torrent.org/source/deluge-" + self.version + ".tar.gz", shell = True)
        subprocess.check_call("tar xf deluge-" + self.version + ".tar.gz", shell = True)

    def installDeluge(self):
        os.chdir("/root/deluge-" + self.version)
        subprocess.check_call("python setup.py build", shell = True)
        subprocess.check_call("python setup.py install", shell = True)
        return
    
    def startDeluge(self):
        subprocess.check_call(
            "deluged", shell = True)
        subprocess.check_call(
            "deluge-web -f", shell = True)

    def openPort(self):
        subprocess.check_call(
            "iptables -I INPUT -p tcp --dport 8112 -j ACCEPT", shell=True)
        return

# ServerSpeeder and BBR
class SpeederBBR(object):
    #Unfinish
    def __init__(self):
        return

    def getCompatibleKernelInfo(self):
        try:
            url = "https://raw.githubusercontent.com/0oVicero0/serverSpeeder_kernel/master/serverSpeeder.txt"
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
        except urllib2.URLError:
            pass
        text = response.read()
        return text

    def checkKernel(self, module="LotServer"):
        kernels = platform.uname()
        kernel = kernels[2]
        if module == "LotServer":
            if kernel not in self.getCompatibleKernelInfo():
                self.changeKernel()
            self.installServerSpeeder()
        elif module == "BBR":
            version = kernel.split(".")
            if not version[0] == '4' and int(version[1]) >= 9:
                self.changeKernel("BBR")
            self.enableBBR()
        return

    def changeKernel(self, module = "LotServer"):
        if module == "LotServer":
            subprocess.check_call("rpm -ivh https://buildlogs.centos.org/c7.01.u/kernel/20150327030147/3.10.0-229.1.2.el7.x86_64/kernel-3.10.0-229.1.2.el7.x86_64.rpm", shell = True)
            output = subprocess.check_output("rpm -qa | grep kernel", shell = True)
            if "3.10.0-229.1.2.el7.x86_64" not in output:
                print "Install kernel error."
                exit(1)
            subprocess.check_call("reboot")

        elif module == "BBR":
            #ELRepo
            subprocess.check_call("rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org", shell = True)
            subprocess.check_call("rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm", shell = True)
            #Kernel
            subprocess.check_call("yum --enablerepo=elrepo-kernel install kernel-ml -y", shell = True)
            output1 = subprocess.check_output("rpm -qa | grep kernel", shell = True)
            if "elrepo" not in output1:
                print "Install kernel error"
                exit(1)
            subprocess.check_call("grub2-set-default 0", shell = True)
            subprocess.check_call("reboot")
        return

    def installServerSpeeder(self):
        url = "https://raw.githubusercontent.com/0oVicero0/serverSpeeder_Install/master/appex.sh"
        output = subprocess.check_output("wget --no-check-certificate -O appex.sh " + url + " && chmod +x appex.sh && bash appex.sh install", shell = True)
        if "Running" not in output:
            print "Install ServerSpeeder error"
            exit(1)
        return

    def enableBBR(self):
        subprocess.check_call("echo 'net.core.default_qdisc=fq' | sudo tee -a /etc/sysctl.conf", shell = True)
        subprocess.check_call("echo 'net.ipv4.tcp_congestion_control=bbr' | sudo tee -a /etc/sysctl.conf", shell = True)
        subprocess.check_call("sysctl -p", shell = True)
        output = subprocess.check_output("sysctl -n net.ipv4.tcp_congestion_control", shell = True)
        if "bbr" not in output:
            print "Enable BBR error"
            exit(1)
        return

class ArgvHandler(object):
    parser = argparse.ArgumentParser(description="CentOS 7 Seedbox Easy Installation Script")

    def __init__(self):
        ArgvHandler.addUsername()
        ArgvHandler.addPassword()
        ArgvHandler.addQbittorrentArg()
        ArgvHandler.addDelugeArg()
        ArgvHandler.addRtorrentArg()
        ArgvHandler.parser.parse_args()

        global password, username
        password = ArgvHandler.getArgv().password
        username = ArgvHandler.getArgv().username
        return

    @classmethod
    def getArgv(cls):
        return ArgvHandler.parser.parse_args()

    @classmethod
    def addPassword(cls):
        cls.parser.add_argument(
            "-p", "--password", nargs = "?", const = ''.join(random.sample(string.ascii_letters + string.digits, 16)), action = "store", 
            dest = "password")
        return

    @classmethod
    def addUsername(cls):
        cls.parser.add_argument(
            "-u", "--username", nargs = "?", const = platform.node(), action = "store", 
            dest = "username")
        return

    @classmethod
    def addQbittorrentArg(cls):
        cls.parser.add_argument(
            "-q", "--qbittorrent", nargs = "?", const = "4.0.4", action = "store", help = "Enable Qbittorrent installation", 
            dest = "qbver")
        return

    @classmethod
    def addDelugeArg(cls):
        cls.parser.add_argument(
            "-d", "--deluge", nargs = "?", const = "1.3.15", action = "store", help = "Enable Deluge installation", 
            dest = "dever")
        return

    @classmethod
    def addRtorrentArg(cls):
        cls.parser.add_argument(
            "-r", "--rtorrent", nargs = "?", const = "0.9.6", action = "store", help = "Enable Rtorrent and Rutorrent installation", 
            dest = "rtver")

    @classmethod
    def dealArgv(cls):
        return

class ShellInterfaceHandler(object):
    def __init__(self):
        self.showMenu()
        return

    def showMenu(self):
        for value in ArgvHandler.getArgv().__dict__.values():
            if value:
                ArgvHandler.dealArgv()
                return

        while True:
            print "1.Install Deluge"
            print "2.Install Qbittorrent"
            print "3.Install Rtorrent and Rutorrent"
            print "4.Install QB(4.0.4) RT(0.9.6/0.13.6) DE(1.3.15)"
            print "0.Exit"
            self.option = raw_input("Please input your options: ")
            self.processInput(int(self.option))

    def processInput(self, option = 4):
        if option == 0:
            exit(0)
        if option == 1:
            version = raw_input("Please input the version you want to install[1.3.15]: ")
            if version.strip() == "":
                Deluge("1.3.15")
            else:
                Deluge(version)

        elif option == 2:
            version = raw_input("Please input the version you want to install[4.0.4]: ")
            if version.strip() == "":
                Qbittorrent("4.0.4")
            else:
                Qbittorrent(version)
        
        elif option == 3:
            rversion = raw_input("Please input the rtorrent version you want to install[0.9.6]: ")
            if version.strip() == "":
                Rtorrent()
            else:
                libversions = rversion.split(".")
                libversion = "0.13." + libversions[:-1]
                Rtorrent(rversion, libversion)

        elif option == 4:
            Deluge()
            Qbittorrent()
            Rtorrent()

        else:
            print "Invalid input."
            return

        print "Installation complete.\nPlease start qbittorrent-nox mannully\nexit program..."
        time.sleep(5)
        exit(0)
        return

    def showInstallationInfo(self):
        return

            

def main():
    ArgvHandler()
    SysRelated()
    ShellInterfaceHandler()



if __name__ == "__main__":
    main()
