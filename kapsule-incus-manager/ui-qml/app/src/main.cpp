#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "kimclient.h"
#include "containersmodel.h"
#include "networksmodel.h"
#include "storagemodel.h"
#include "imagesmodel.h"
#include "profilesmodel.h"
#include "eventsource.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setOrganizationName("KapsuleIncusManager");
    app.setOrganizationDomain("kapsule-incus-manager.org");
    app.setApplicationName("Kapsule Incus Manager");
    app.setApplicationVersion("0.1.0");

    qmlRegisterType<KIM::KimClient>      ("KIM", 1, 0, "KimClient");
    qmlRegisterType<KIM::ContainersModel>("KIM", 1, 0, "ContainersModel");
    qmlRegisterType<KIM::NetworksModel>  ("KIM", 1, 0, "NetworksModel");
    qmlRegisterType<KIM::StorageModel>   ("KIM", 1, 0, "StorageModel");
    qmlRegisterType<KIM::ImagesModel>    ("KIM", 1, 0, "ImagesModel");
    qmlRegisterType<KIM::ProfilesModel>  ("KIM", 1, 0, "ProfilesModel");
    qmlRegisterType<KIM::EventSource>    ("KIM", 1, 0, "EventSource");

    QQmlApplicationEngine engine;

    const QUrl url(u"qrc:/KIM/qml/Main.qml"_qs);
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed,
        &app, [](const QUrl &) { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);

    engine.load(url);
    return app.exec();
}
