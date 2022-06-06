#include <thread>
#include <future>
#include <algorithm>
#include "PeopleDetector.hpp"
#include "processRequest.hpp"

using json = nlohmann::json;


bool hasPeopleFilter(size_t numberOfPeople, bool hasPeople){
    if(hasPeople && numberOfPeople > 0){
        return true;
    }
    else if(!hasPeople && numberOfPeople == 0){
        return true;
    }
    return false;
}

bool minPeopleFilter(size_t numberOfPeople, int minPeople){
    return (numberOfPeople >= minPeople);
}

bool maxPeopleFilter(size_t numberOfPeople, int maxPeople){
    return (numberOfPeople <= maxPeople);
}

bool isNumber(const std::string& str)
{
    for(char const& c : str) {
        if(!std::isdigit(c))
            return false;
    }
    return true;
}

#include <iostream>
std::vector<std::string> filterImages(PeopleDetector&& peopleDetector,
                                      const std::vector<std::string>& paths,
                                      const json& options){
    auto hasPeople = options["hasPeople"];
    auto minPeople = options["minPeople"];
    auto maxPeople = options["maxPeople"];

    std::vector<std::string> result;
    for(const auto& path : paths){
        size_t numberOfPeople = peopleDetector.countPeople(path);

        if(hasPeople.is_string() && !hasPeopleFilter(numberOfPeople, hasPeople.get<std::string>() == "true")){
            std::string hasPeopleStr = hasPeople.get<std::string>();
            if(hasPeopleStr == "true" && !hasPeopleFilter(numberOfPeople, true)){
                continue;
            }
            else if(hasPeopleStr == "false" && !hasPeopleFilter(numberOfPeople, false)){
                continue;
            }
        }
        if(minPeople.is_string()){
            std::string minPeopleStr = minPeople.get<std::string>();
            if(isNumber(minPeopleStr) && !minPeopleFilter(numberOfPeople, std::stoi(minPeopleStr))){
                continue;
            }
        }
        if(maxPeople.is_string()){
            std::string maxPeopleStr = maxPeople.get<std::string>();
            if(isNumber(maxPeopleStr) && !maxPeopleFilter(numberOfPeople, std::stoi(maxPeopleStr))){
                continue;
            }
        }
        result.push_back(path);
    }
    return result;
}

std::vector<std::string> processJsonRequest(const cv::FileStorage& cascadeFile, const json& reqJson){
    auto paths = reqJson["paths"].get<std::vector<std::string>>();
    json options = reqJson["params"];

    return filterImages(PeopleDetector(cascadeFile.getFirstTopLevelNode()), paths, options);
}

std::vector<std::string> processJsonRequestParallel(const cv::FileStorage& cascadeFile,
                                                    const json& reqJson,
                                                    int threadsNumber){
    auto paths = reqJson["paths"].get<std::vector<std::string>>();
    json options = reqJson["params"];

    // divide paths vector into portions for each thread
    const size_t elements = std::max<size_t>(1, paths.size() / threadsNumber);
    std::vector<std::vector<std::string>> data(std::min<size_t>(paths.size(), threadsNumber));
    for(int i = 0; i < data.size(); i++){
        std::move(paths.begin() + i*elements, paths.begin() + (i+1)*elements, std::back_inserter(data.at(i)));
    }
    std::move(paths.begin() + data.size()*elements, paths.end(), std::back_inserter(data.at(0)));

    // run async threads
    std::vector<std::future<std::vector<std::string>>> futures(data.size());
    for(int i=0; i < data.size(); i++){
        PeopleDetector peopleDetector(cascadeFile.getFirstTopLevelNode());
        futures.at(i) = std::async(std::launch::async, filterImages,
                                   std::move(peopleDetector), std::cref(data.at(i)), std::cref(options));
    }

    // get results from threads
    std::vector<std::string> result;
    for(auto& future : futures){
        auto resultPart = future.get();
        std::move(resultPart.begin(), resultPart.end(), std::back_inserter(result));
    }
    return result;
}
