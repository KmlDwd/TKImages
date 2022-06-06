#ifdef _WIN32
#define NOMINMAX 1
#endif

#include <iostream>
#include <amqpcpp.h>
#include <nlohmann/json.hpp>
#include <Poco/Net/NetException.h>
#include "INIReader.h"
#include "SimplePocoHandler.h"
#include "processRequest.hpp"
#include "PeopleDetector.hpp"

using json = nlohmann::json;

int main(){
    const std::string cascadePath = "cascades/haarcascade_frontalface_default.xml";
    cv::FileStorage cascadeFile(cascadePath, cv::FileStorage::READ);
    if(!cascadeFile.isOpened()){
        std::cerr << "could not open " << cascadePath << " file\n";
        return -1;
    }

    const std::string iniPath = "config.ini";
    INIReader reader(iniPath);
    if (reader.ParseError() < 0) {
        std::cout << "Can't load " << iniPath << '\n';
        return -1;
    }
    const std::string section = "RABBITMQ";
    const std::string address = reader.Get(section, "address", "localhost");
    const int port = reader.GetInteger(section, "port", 5672);
    const std::string user = reader.Get(section, "username", "user");
    const std::string password = reader.Get(section, "password", "password");
    const std::string queue_name = reader.Get(section, "queue_name", "image_finder.people");
    const std::string results_queue_name = reader.Get(section, "results_queue_name", "image_finder.results");

    try{
        SimplePocoHandler handler(address, port);
        AMQP::Connection connection(&handler, AMQP::Login(user, password), "/");

        AMQP::Channel channel(&connection);
        channel.declareQueue(queue_name);
        channel.consume(queue_name).onReceived(
                [&channel, &results_queue_name, &cascadeFile]
                (const AMQP::Message &message, uint64_t deliveryTag, bool redelivered) {
                    channel.ack(deliveryTag);
                    std::string messageBody(message.body(), message.body() + message.bodySize());
                    json request = json::parse(messageBody);
                    std::cout << "Received message: " << request.dump(4) << '\n';

                    auto filteredPaths = processJsonRequestParallel(cascadeFile, request);
                    json response = {
                        {"result", 200},
                        {"paths", filteredPaths},
                        {"total", filteredPaths.size()},
                        {"sender", "people_service"}
                    };

                    std::cout << "Sending response: " << response.dump(4) << std::endl;
                    channel.publish("", results_queue_name, response.dump());
                });

        std::cout << "Waiting for messages. To exit press CTRL-C" << std::endl;
        handler.loop();
    }
    catch(Poco::Net::ConnectionRefusedException e){
        std::cout << e.what() << '\n';
    }

    return 0;
}