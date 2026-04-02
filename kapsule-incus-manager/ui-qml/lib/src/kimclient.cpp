#include "kimclient.h"
#include <QDBusConnection>
#include <QDBusReply>

namespace KIM {

static constexpr auto DBUS_SERVICE   = "org.KapsuleIncusManager";
static constexpr auto DBUS_PATH      = "/org/KapsuleIncusManager";
static constexpr auto DBUS_INTERFACE = "org.KapsuleIncusManager";

KimClient::KimClient(QObject *parent)
    : QObject(parent)
{
    connectToDaemon();
}

KimClient::~KimClient() = default;

bool KimClient::isConnected() const
{
    return m_connected;
}

void KimClient::connectToDaemon()
{
    m_iface = new QDBusInterface(
        DBUS_SERVICE, DBUS_PATH, DBUS_INTERFACE,
        QDBusConnection::sessionBus(), this);

    m_connected = m_iface->isValid();
    emit connectedChanged(m_connected);

    if (m_connected) {
        QDBusConnection::sessionBus().connect(
            DBUS_SERVICE, DBUS_PATH, DBUS_INTERFACE,
            "EventReceived", this, SIGNAL(eventReceived(QVariantMap)));
    }
}

void KimClient::listInstances(const QString &project, const QString &remote)
{
    auto reply = m_iface->asyncCall("ListInstances", project, remote);
    // TODO: connect watcher to emit instancesListed
    Q_UNUSED(reply)
}

void KimClient::createInstance(const QVariantMap &config)
{
    m_iface->asyncCall("CreateInstance", config);
}

void KimClient::startInstance(const QString &name, const QString &project)
{
    m_iface->asyncCall("StartInstance", name, project);
}

void KimClient::stopInstance(const QString &name, bool force, const QString &project)
{
    m_iface->asyncCall("StopInstance", name, force, project);
}

void KimClient::restartInstance(const QString &name, bool force, const QString &project)
{
    m_iface->asyncCall("RestartInstance", name, force, project);
}

void KimClient::freezeInstance(const QString &name, const QString &project)
{
    m_iface->asyncCall("FreezeInstance", name, project);
}

void KimClient::deleteInstance(const QString &name, bool force, const QString &project)
{
    m_iface->asyncCall("DeleteInstance", name, force, project);
}

void KimClient::renameInstance(const QString &name, const QString &newName,
                               const QString &project)
{
    m_iface->asyncCall("RenameInstance", name, newName, project);
}

void KimClient::listNetworks(const QString &project)
{
    m_iface->asyncCall("ListNetworks", project);
}

void KimClient::createNetwork(const QVariantMap &config)
{
    m_iface->asyncCall("CreateNetwork", config);
}

void KimClient::deleteNetwork(const QString &name)
{
    m_iface->asyncCall("DeleteNetwork", name);
}

void KimClient::listStoragePools()
{
    m_iface->asyncCall("ListStoragePools");
}

void KimClient::createStoragePool(const QVariantMap &config)
{
    m_iface->asyncCall("CreateStoragePool", config);
}

void KimClient::deleteStoragePool(const QString &name)
{
    m_iface->asyncCall("DeleteStoragePool", name);
}

void KimClient::listImages(const QString &remote)
{
    m_iface->asyncCall("ListImages", remote);
}

void KimClient::pullImage(const QString &remote, const QString &fingerprint)
{
    m_iface->asyncCall("PullImage", remote, fingerprint);
}

void KimClient::deleteImage(const QString &fingerprint)
{
    m_iface->asyncCall("DeleteImage", fingerprint);
}

void KimClient::listProfiles(const QString &project)
{
    m_iface->asyncCall("ListProfiles", project);
}

void KimClient::createProfile(const QVariantMap &config)
{
    m_iface->asyncCall("CreateProfile", config);
}

void KimClient::deleteProfile(const QString &name)
{
    m_iface->asyncCall("DeleteProfile", name);
}

void KimClient::listProjects()
{
    m_iface->asyncCall("ListProjects");
}

void KimClient::createProject(const QVariantMap &config)
{
    m_iface->asyncCall("CreateProject", config);
}

void KimClient::deleteProject(const QString &name)
{
    m_iface->asyncCall("DeleteProject", name);
}

void KimClient::listClusterMembers()
{
    m_iface->asyncCall("ListClusterMembers");
}

void KimClient::listRemotes()
{
    m_iface->asyncCall("ListRemotes");
}

void KimClient::addRemote(const QVariantMap &config)
{
    m_iface->asyncCall("AddRemote", config);
}

void KimClient::removeRemote(const QString &name)
{
    m_iface->asyncCall("RemoveRemote", name);
}

void KimClient::listOperations()
{
    m_iface->asyncCall("ListOperations");
}

void KimClient::cancelOperation(const QString &id)
{
    m_iface->asyncCall("CancelOperation", id);
}

} // namespace KIM
