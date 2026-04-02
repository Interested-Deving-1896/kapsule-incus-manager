#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "kimclient.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setOrganizationName("KapsuleIncusManager");
    app.setOrganizationDomain("kapsule-incus-manager.org");
    app.setApplicationName("Kapsule Incus Manager");
    app.setApplicationVersion("0.1.0");

    qmlRegisterType<KIM::KimClient>("KIM", 1, 0, "KimClient");

    QQmlApplicationEngine engine;

    const QUrl url(u"qrc:/KIM/qml/Main.qml"_qs);
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed,
        &app, [](const QUrl &) { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);

    engine.load(url);
    return app.exec();
}
