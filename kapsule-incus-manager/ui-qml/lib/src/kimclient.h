#pragma once

#include "types.h"
#include <QObject>
#include <QDBusInterface>

namespace KIM {

// D-Bus client for the KIM daemon.
// Exposes the full daemon API as Qt signals and slots.
// License: LGPL-2.1-or-later
class KimClient : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)

public:
    explicit KimClient(QObject *parent = nullptr);
    ~KimClient() override;

    bool isConnected() const;

    // Containers / VMs
    Q_INVOKABLE void listInstances(const QString &project = QString(),
                                   const QString &remote  = QString());
    Q_INVOKABLE void createInstance(const QVariantMap &config);
    Q_INVOKABLE void startInstance(const QString &name, const QString &project = QString());
    Q_INVOKABLE void stopInstance(const QString &name, bool force = false,
                                  const QString &project = QString());
    Q_INVOKABLE void restartInstance(const QString &name, bool force = false,
                                     const QString &project = QString());
    Q_INVOKABLE void freezeInstance(const QString &name, const QString &project = QString());
    Q_INVOKABLE void deleteInstance(const QString &name, bool force = false,
                                    const QString &project = QString());
    Q_INVOKABLE void renameInstance(const QString &name, const QString &newName,
                                    const QString &project = QString());

    // Networks
    Q_INVOKABLE void listNetworks(const QString &project = QString());
    Q_INVOKABLE void createNetwork(const QVariantMap &config);
    Q_INVOKABLE void deleteNetwork(const QString &name);

    // Storage
    Q_INVOKABLE void listStoragePools();
    Q_INVOKABLE void createStoragePool(const QVariantMap &config);
    Q_INVOKABLE void deleteStoragePool(const QString &name);

    // Images
    Q_INVOKABLE void listImages(const QString &remote = QString());
    Q_INVOKABLE void pullImage(const QString &remote, const QString &fingerprint);
    Q_INVOKABLE void deleteImage(const QString &fingerprint);

    // Profiles
    Q_INVOKABLE void listProfiles(const QString &project = QString());
    Q_INVOKABLE void createProfile(const QVariantMap &config);
    Q_INVOKABLE void deleteProfile(const QString &name);

    // Projects
    Q_INVOKABLE void listProjects();
    Q_INVOKABLE void createProject(const QVariantMap &config);
    Q_INVOKABLE void deleteProject(const QString &name);

    // Cluster
    Q_INVOKABLE void listClusterMembers();

    // Remotes
    Q_INVOKABLE void listRemotes();
    Q_INVOKABLE void addRemote(const QVariantMap &config);
    Q_INVOKABLE void removeRemote(const QString &name);

    // Operations
    Q_INVOKABLE void listOperations();
    Q_INVOKABLE void cancelOperation(const QString &id);

signals:
    void connectedChanged(bool connected);

    // Async responses
    void instancesListed(const QVariantList &instances);
    void instanceCreated(const QString &name);
    void instanceStateChanged(const QString &name, const QString &status);
    void instanceDeleted(const QString &name);

    void networksListed(const QVariantList &networks);
    void storagePoolsListed(const QVariantList &pools);
    void imagesListed(const QVariantList &images);
    void profilesListed(const QVariantList &profiles);
    void projectsListed(const QVariantList &projects);
    void clusterMembersListed(const QVariantList &members);
    void remotesListed(const QVariantList &remotes);
    void operationsListed(const QVariantList &operations);

    // Real-time events from daemon fan-out
    void eventReceived(const QVariantMap &event);

    void error(const QString &message);

private:
    QDBusInterface *m_iface = nullptr;
    bool            m_connected = false;

    void connectToDaemon();
};

} // namespace KIM
